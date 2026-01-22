#!/usr/bin/env python
"""Create tables for the report."""
import json
from pathlib import Path
import re

import anytree
import pandas as pd
from workflow_glue.report_utils.report_utils import (
    RANK_ORDER,
    RANK_REPORT_ABB,
    RANKS_ABB,
)
from .util import wf_parser  # noqa: ABS101


def fill_down_to_rank(root, target_rank):
    """
    Extend leaf nodes to the target taxonomic rank with placeholder names.

    For each leaf node with a rank < target_rank, create intermediate nodes
    down to target_rank. Placeholder names include the rank abbreviation as a suffix
    (e.g., 'Unclassified_Genus_(o)') to indicate unclassified taxa at those levels.
    :param root(tree): tree
    :param target_rank (str): requested rank
    :return: tree
    """
    suffix_re = re.compile(r"(_\([dkpcofgs]\))$")  # match _(o)
    for node in anytree.PreOrderIter(root):
        if node.rank is None:
            continue

        if node.children or node.rank >= target_rank:
            continue

        parent = node

        # Keeps name if it already has a suffix
        if suffix_re.search(node.name):
            placeholder_name = node.name
        else:
            base = node.name
            if base.startswith("Unclassified_"):
                base = base.replace("Unclassified_", "", 1)
            # For unclassified nodes, use parent's rank as the suffix
            # (unclassified nodes lack their own rank)
            if (
                node.name.startswith("Unclassified_")
                and node.parent
                and node.parent.rank is not None
            ):
                suffix = node.parent.rank
            else:
                suffix = node.rank

            suffix = f"_({RANK_REPORT_ABB[suffix]})"
            placeholder_name = f"Unclassified_{base}{suffix}"

        # Fill down by adding the new name
        parent = node
        for r in range(node.rank + 1, target_rank + 1):
            parent = anytree.Node(
                placeholder_name,
                parent=parent,
                rank=r,
                count=node.count
            )

    return root


# READ INPUT DATA
def parse_lineages(lineages):
    """Join lineage counts into a df for a particular taxonomic rank.

    :param lineages (str): String indicating the path of the dir with the json.
        For kraken2 is a folder/folder/*.json and for minimap2 is folder/*.json
    :return (dict): Taxa counts in json structure.
    """
    path_to_json = lineages
    json_files = list(Path(path_to_json).glob('*.json'))
    all_json = {}
    for i in json_files:
        with open(i) as json_file:
            all_json.update(json.load(json_file))
    if any(list(all_json.values())):
        return all_json
    else:
        return None  # no reads at all (e.g. bracken threshold)


# PREPARE INPUT DATA

def tax_tree(lineage_trees_dict):
    """From lineages json, create a dictionary with {sample:tree (counts per lineage)}.

    Save the full taxonomy string.

    :param lineage_trees_dict (dict): Taxa counts in json structure. Nested dictionary.
        {"Sample": {"Taxon name":{"rank":str, "count":int, "children": dict},}}.
    :return (dict): Dictionary with one lineage tree per sample.
    """
    # Root project
    trees = {}
    for sample_id, lineage_sample in lineage_trees_dict.items():
        # Root sample
        rootnode = anytree.Node("root", rank=None, count=0, sample=None)

        def itertaxa(d, parent=None, parent_node=None):
            """From lineages json, construct a tree with the counts per each taxon.

            :param d (dict): Taxa counts in json structure. Nested dictionary:
                {"Taxon":{"rank":str, "count":int, "children": {}}}}.
            :param parent (str): Name of the parent taxon.
            :param parent_node (Node): Node with the info related to the parent taxon.
            """
            for taxon, taxon_data in d.items():
                if parent:
                    # Databases don't always follow a perfect structure.
                    # Check that parent belongs to immediate previous rank
                    # to avoid those cases in which some ranks are missing
                    # (e.g.: Wohlfahrtiimonas)
                    diff_ranks = RANK_ORDER[taxon_data['rank']] - parent_node.rank
                    if diff_ranks == 1:  # Consecutive ranks
                        if 'uncultured' not in taxon:
                            node = anytree.Node(
                                taxon, parent=parent_node,
                                count=taxon_data['count'],
                                rank=RANK_ORDER[taxon_data['rank']],
                            )
                        else:
                            # Keep the name of the previous rank to avoid duplicates
                            node = anytree.Node(
                                f'{parent_node.name}_uncultured',
                                parent=parent_node,
                                count=taxon_data['count'],
                                rank=(parent_node.rank + 1)
                                )
                    else:  # Add missing ranks
                        original_parent_node = parent_node
                        for i in range(1, diff_ranks):
                            # Fill missing ranks with label: Incertae sedis,
                            # i.e. https://en.wikipedia.org/wiki/Wohlfahrtiimonas
                            label = 'Incertae_sedis'
                            if (
                                original_parent_node.name.endswith('Bacteria') or
                                    original_parent_node.name.endswith('Archaea')):
                                # Leave in blank
                                node = anytree.Node(
                                    f'{parent_node.name}_none',
                                    parent=parent_node,
                                    count=taxon_data['count'],
                                    rank=(parent_node.rank + 1)
                                    )
                            elif 'Unclassified' not in original_parent_node.name:
                                # dont' repeat label if it is already there
                                if label in parent_node.name:
                                    node = anytree.Node(
                                        parent_node.name,
                                        parent=parent_node,
                                        count=taxon_data['count'],
                                        rank=(parent_node.rank + 1)
                                        )
                                else:
                                    node = anytree.Node(
                                        f'{parent_node.name}_{label}',
                                        parent=parent_node,
                                        count=taxon_data['count'],
                                        rank=(parent_node.rank + 1)
                                        )
                            else:  # Do not do this for Unclassified
                                node = anytree.Node(
                                    taxon,
                                    parent=parent_node,
                                    count=taxon_data['count'],
                                    rank=(parent_node.rank + 1)
                                    )
                            parent_node = node
                        # Add last identified rank
                        node = anytree.Node(
                            taxon, parent=node,
                            count=taxon_data['count'],
                            rank=RANK_ORDER[taxon_data['rank']]
                            )
                        # Return to original parent node
                        parent_node = original_parent_node
                else:
                    # could happen that these nodes are directly species without parent
                    # custom refs added to db: e.g.: synthetic Vaccinia virus
                    if taxon_data['rank'] == 'superkingdom':
                        node = anytree.Node(
                            taxon, parent=rootnode,
                            count=taxon_data['count'],
                            rank=RANK_ORDER[taxon_data['rank']]
                            )
                    else:
                        # add it as the higher rank and copy it in downstrain levels
                        node = anytree.Node(
                            taxon, parent=rootnode,
                            count=taxon_data['count'],
                            rank=RANK_ORDER['superkingdom']
                            )
                        # repeat the node
                        taxon_data['children'] = {
                            taxon: {
                                "rank": taxon_data['rank'],
                                "count": taxon_data['count'],
                                "children": {}
                            }}
                if isinstance(taxon_data['children'], dict):
                    itertaxa(taxon_data['children'], parent=taxon, parent_node=node)

        itertaxa(lineage_sample)
        trees[sample_id] = rootnode
    return trees


def check_counts(taxa_trees):
    """Verify that more general taxonomic ranks contains counts from more specific ones.

    Otherwise, add an 'Unclassified_<taxon>' Node to not miss those counts.

    :param taxa_trees (anytree.Node): Tree structure with a rootnode (the sample)
        and children nodes following the lineage structure.
    :return (dict): Tree structure with a rootnode (the sample)
        and children nodes following the lineage structure.
    """
    # TODO: This shouln't happen from bracken report, but allow this in future?.
    # Total counts per node == sum(counts of children nodes), i.e. [in counts]:
    # Gammaproteobacteria (c) = Enterobacterales (o) + found Order (o)
    # If not:
    # Gammaproteobacteria_unclassified (o) = Gammaproteobacteria (c) - sum(found order)
    for node in anytree.PreOrderIter(taxa_trees, maxlevel=taxa_trees.height):
        if sum([n.count for n in node.children]) != node.count:
            # Add unclassified node
            if not re.match('^Unclassified|^root', node.name):
                unclassified_taxon = (
                    f"Unclassified_{node.name}_({RANK_REPORT_ABB[node.rank]})"
                )
                counts = node.count - sum([n.count for n in node.children])
                anytree.Node(
                    unclassified_taxon, parent=node, rank=node.rank + 1, count=counts)
    return taxa_trees


def prepare_taxa_table(taxa_tree, rank):
    """Filter the abundance table for a specific rank.

    :param sample_taxa_tree (anytree.Node): Node with counts for all possible ranks.
    :param rank (str): Index of the taxonomic rank to use as filter.
    :return (DataFrame): DataFrame with counts per specific rank for one sample.
    """
    # Make df from anytree.Node
    d = []
    for node in anytree.search.findall(taxa_tree, lambda node: node.rank == rank):
        d.append(
            {
                'rank': node.rank,
                'count':  node.count,
                'tax': ';'.join([str(node.name) for node in node.path[1:]])
            }
        )
    # If the rank level does not exist, return None
    if d:
        df = pd.DataFrame(d)
        return df
    else:
        return None


def join_abundance_tables(taxa_trees, rank):
    """Take taxonomy trees and create a dataframe from them.

    :param taxa_trees (dict): Dictionary with one lineage tree per sample.
    :param rank (str): Taxonomic rank to subset the df.

    :return (DataFrame): Table with counts per specific rank for all the samples.
    """
    # Trees into tables
    tables = {}
    target_rank_int = RANK_ORDER[rank]
    for s, t in taxa_trees.items():
        t2 = check_counts(t)
        t2 = fill_down_to_rank(t2, target_rank_int)
        tables[s] = prepare_taxa_table(t2, target_rank_int)

    tables = {k: v for k, v in tables.items() if v is not None}
    if not tables:
        return pd.DataFrame(columns=["tax", "total"])

    df_all = pd.concat(list(tables.values()), keys=list(tables.keys()))
    # Remove multiindex
    df_all_samples = df_all.reset_index().rename(columns={'level_0': 'sample'})
    # Pivot table. Make each sample a different column
    df = df_all_samples.pivot_table(
        columns=['sample'], values='count', index=['tax'], fill_value=0)
    df['total'] = df.sum(axis=1)
    df = df.sort_values('total', ascending=False).reset_index()
    df.columns.name = None
    return df


def main(args):
    """Run the entry point."""
    # Join taxonomy data
    all_json = parse_lineages(args.lineages)
    rank = RANKS_ABB[args.taxonomic_rank]
    if all_json:
        # Extract all possible lineages
        allranks_tree = tax_tree(all_json)
        # join last abundance table
        counts_per_taxa = join_abundance_tables(allranks_tree, rank).set_index('tax')
        counts_per_taxa.to_csv(f'abundance_table_{rank}.tsv', sep='\t')
    else:
        # Return empty file
        with open(f'abundance_table_{rank}.tsv', 'w') as empty_output:
            empty_output.write("tax\tsample\tcount\ttotal\n")


def argparser():
    """Argument parser for entrypoint."""
    parser = wf_parser("abundance_tables")
    parser.add_argument(
        "--lineages", help="JSON files or directory containing JSON files.",
        type=Path
    )
    parser.add_argument(
        "--taxonomic_rank", help="Taxonomic rank.")
    return parser
