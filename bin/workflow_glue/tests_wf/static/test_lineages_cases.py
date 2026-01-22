"""Test cases."""
# String fixtures for pytest:
# - JSON strings can be loaded with json.loads(TEST_1_JSON)
# - DF strings can be loaded with pandas.read_csv(io.StringIO(TEST_1_DF), sep="\t")

# -------------------------
# TEST 1: one lineage complete at genus, request genus
# Ideal case. Simplification: 2 taxa from the same family
# Expect: 2 taxa at genus appear with counts.
# -------------------------

TEST_1_JSON_ALL_RANKS = r"""{
  "barcode01": {
    "Eukaryota": {
      "rank": "superkingdom",
      "count": 4,
      "children": {
        "Fungi": {
          "rank": "kingdom",
          "count": 4,
          "children": {
            "Ascomycota": {
              "rank": "phylum",
              "count": 4,
              "children": {
                "Saccharomycetes": {
                  "rank": "class",
                  "count": 4,
                  "children": {
                    "Saccharomycetales": {
                      "rank": "order",
                      "count": 4,
                      "children": {
                        "Saccharomycetaceae": {
                          "rank": "family",
                          "count": 4,
                          "children": {
                            "Candida": {
                              "rank": "genus",
                              "count": 3,
                              "children": {}
                            },
                            "Saccharomyces": {
                              "rank": "genus",
                              "count": 1,
                              "children": {}
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}"""

TEST_1_DF_ALL_RANKS = r"""tax	barcode01	total
Eukaryota;Fungi;Ascomycota;Saccharomycetes;Saccharomycetales;Saccharomycetaceae;Candida	3	3
Eukaryota;Fungi;Ascomycota;Saccharomycetes;Saccharomycetales;Saccharomycetaceae;Saccharomyces	1	1
"""  # noqa: E501


# -------------------------
# TEST 2: incomplete lineage, request genus
# Real world case: Eukaryota lineages in SILVA: veneroida #HELP-10128
# Simplification: 1 taxon
# Expect: order appears at genus via placeholders Unclassified_Enterobacterales_(o)
# -------------------------
TEST_2_JSON_INCOMPLETE_LIN = r"""{
  "barcode01": {
    "Bacteria": {
      "rank": "superkingdom",
      "count": 10,
      "children": {
        "Proteobacteria": {
          "rank": "phylum",
          "count": 10,
          "children": {
            "Gammaproteobacteria": {
              "rank": "class",
              "count": 10,
              "children": {
                "Enterobacterales": {
                  "rank": "order",
                  "count": 10,
                  "children": {}
                }
              }
            }
          }
        }
      }
    }
  }
}"""

TEST_2_DF_INCOMPLETE_LIN = r"""tax	barcode01	total
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Enterobacterales;Unclassified_Enterobacterales_(o);Unclassified_Enterobacterales_(o)	10	10
"""  # noqa: E501


# -------------------------
# TEST 3: mixed completeness within the same order.
# Real world case +: Eukaryota lineages in SILVA: veneroida #HELP-10128
# Simplification: 1 taxon
# Expect: order appears at genus via placeholders Unclassified_Enterobacterales_(o)
# -------------------------
TEST_3_JSON_MIXED_COMPLETENESS_ORDERS = r"""{
  "barcode01": {
    "Bacteria": {
      "rank": "superkingdom",
      "count": 30,
      "children": {
        "Proteobacteria": {
          "rank": "phylum",
          "count": 30,
          "children": {
            "Gammaproteobacteria": {
              "rank": "class",
              "count": 30,
              "children": {
                "Enterobacterales": {
                  "rank": "order",
                  "count": 20,
                  "children": {
                    "Enterobacteriaceae": {
                      "rank": "family",
                      "count": 12,
                      "children": {
                        "Escherichia": {
                          "rank": "genus",
                          "count": 7,
                          "children": {}
                        },
                        "Klebsiella": {
                          "rank": "genus",
                          "count": 5,
                          "children": {}
                        }
                      }
                    },
                    "Morganellaceae": {
                      "rank": "family",
                      "count": 8,
                      "children": {}
                    }
                  }
                },
                "Pseudomonadales": {
                  "rank": "order",
                  "count": 10,
                  "children": {}
                }
              }
            }
          }
        }
      }
    }
  }
}"""

TEST_3_DF_MIXED_COMPLETENESS_ORDERS = r"""tax	barcode01	total
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Enterobacterales;Enterobacteriaceae;Escherichia	7	7
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Enterobacterales;Enterobacteriaceae;Klebsiella	5	5
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Enterobacterales;Morganellaceae;Unclassified_Morganellaceae_(f)	8	8
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Pseudomonadales;Unclassified_Pseudomonadales_(o);Unclassified_Pseudomonadales_(o)	10	10
"""  # noqa: E501

# -------------------------
# TEST 4: two samples with partially overlapping taxa
# - S1 has Escherichia and Klebsiella (Enterobacteriaceae)
# - S2 has Escherichia (shared) and Salmonella (new taxa not in S1)
# - Klebsiella appears in S1 but not in S2
# - All the taxa have full lineages info, all appear in the table.
# -------------------------
TEST_4_JSON_TWO_SAMPLES_PARTIAL_OVERLAP = r"""{
  "S1": {
    "Bacteria": {
      "rank": "superkingdom",
      "count": 12,
      "children": {
        "Proteobacteria": {
          "rank": "phylum",
          "count": 12,
          "children": {
            "Gammaproteobacteria": {
              "rank": "class",
              "count": 12,
              "children": {
                "Enterobacterales": {
                  "rank": "order",
                  "count": 12,
                  "children": {
                    "Enterobacteriaceae": {
                      "rank": "family",
                      "count": 12,
                      "children": {
                        "Escherichia": {
                          "rank": "genus",
                          "count": 7,
                          "children": {}
                        },
                        "Klebsiella": {
                          "rank": "genus",
                          "count": 5,
                          "children": {}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "S2": {
    "Bacteria": {
      "rank": "superkingdom",
      "count": 10,
      "children": {
        "Proteobacteria": {
          "rank": "phylum",
          "count": 10,
          "children": {
            "Gammaproteobacteria": {
              "rank": "class",
              "count": 10,
              "children": {
                "Enterobacterales": {
                  "rank": "order",
                  "count": 10,
                  "children": {
                    "Enterobacteriaceae": {
                      "rank": "family",
                      "count": 10,
                      "children": {
                        "Escherichia": {
                          "rank": "genus",
                          "count": 4,
                          "children": {}
                        },
                        "Salmonella": {
                          "rank": "genus",
                          "count": 6,
                          "children": {}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}"""

TEST_4_DF_TWO_SAMPLES_PARTIAL_OVERLAP = r"""tax	S1	S2	total
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Enterobacterales;Enterobacteriaceae;Escherichia	7	4	11
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Enterobacterales;Enterobacteriaceae;Klebsiella	5	0	5
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Enterobacterales;Enterobacteriaceae;Salmonella	0	6	6
"""  # noqa: E501

# -------------------------
# TEST 5: incomplete lineage, request different ranks
# - Real world case: Eukaryota lineages in SILVA: veneroida #HELP-10128
# -------------------------
TEST_5_JSON_REAL_SAMPLE = r"""{
  "barcode01": {
    "Eukaryota": {
      "rank": "superkingdom",
      "count": 690,
      "children":{
        "Animalia": {
          "rank": "kingdom",
          "count": 687,
          "children": {
            "Mollusca": {
              "rank": "phylum",
              "count": 684,
              "children": {
                "Bivalvia": {
                  "rank": "class",
                  "count": 684,
                  "children": {
                    "Veneroida": {
                      "rank": "order",
                      "count": 684,
                      "children": {}
                    }
                  }
                }
              }
            },
            "Platyhelminthes": {
              "rank": "phylum",
              "count": 3,
              "children": {
                "Cestoda": {
                  "rank": "class",
                  "count": 3,
                  "children": {
                    "Tetraphyllidea": {
                      "rank": "order",
                      "count": 3,
                      "children": {}
                      }
                    }
                  }
                }
              }
            }
          },
        "Fungi": {
          "rank": "kingdom",
          "count": 1,
          "children": {
            "Basidiomycota": {
              "rank": "phylum",
              "count": 1,
              "children": {
                "Agaricomycetes": {
                  "rank": "class",
                  "count": 1,
                  "children": {
                    "Phallales": {
                      "rank": "order",
                      "count": 1,
                      "children": {
                        "Phallaceae": {
                          "rank": "family",
                          "count": 1,
                          "children": {
                            "Phallus": {
                              "rank": "genus",
                              "count": 1,
                              "children": {}
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "Chloroplastida": {
          "rank": "kingdom",
          "count": 2,
          "children": {
            "Phragmoplastophyta": {
              "rank": "phylum",
              "count": 2,
              "children": {
                "Embryophyta": {
                  "rank": "class",
                  "count": 2,
                  "children": {
                    "Pinales": {
                      "rank": "order",
                      "count": 1,
                      "children": {
                        "Pinus": {
                          "rank": "genus",
                          "count": 1,
                          "children": {}
                        }
                      }
                    },
                    "Malvales": {
                      "rank": "order",
                      "count": 1,
                      "children": {
                        "Gossypium": {
                          "rank": "genus",
                          "count": 1,
                          "children": {}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "Unclassified": {
      "rank": "superkingdom",
      "count": 25,
      "children": {
        "Unknown": {
          "rank": "species",
          "count": 25,
          "children": {}
        }
      }
    }
  }
}
"""


TEST_5_DF_REAL_SAMPLE_SPECIES = r"""tax	barcode01	total
Eukaryota;Animalia;Mollusca;Bivalvia;Veneroida;Unclassified_Veneroida_(o);Unclassified_Veneroida_(o);Unclassified_Veneroida_(o)	684	684
Unclassified;Unknown;Unknown;Unknown;Unknown;Unknown;Unknown;Unknown	25	25
Eukaryota;Animalia;Platyhelminthes;Cestoda;Tetraphyllidea;Unclassified_Tetraphyllidea_(o);Unclassified_Tetraphyllidea_(o);Unclassified_Tetraphyllidea_(o)	3	3
Eukaryota;Chloroplastida;Phragmoplastophyta;Embryophyta;Malvales;Malvales_Incertae_sedis;Gossypium;Unclassified_Gossypium_(g)	1	1
Eukaryota;Fungi;Basidiomycota;Agaricomycetes;Phallales;Phallaceae;Phallus;Unclassified_Phallus_(g)	1	1
Eukaryota;Chloroplastida;Phragmoplastophyta;Embryophyta;Pinales;Pinales_Incertae_sedis;Pinus;Unclassified_Pinus_(g)	1	1
"""  # noqa: E501

TEST_5_DF_REAL_SAMPLE_GENUS = r"""tax	barcode01	total
Eukaryota;Animalia;Mollusca;Bivalvia;Veneroida;Unclassified_Veneroida_(o);Unclassified_Veneroida_(o)	684	684
Unclassified;Unknown;Unknown;Unknown;Unknown;Unknown;Unknown	25	25
Eukaryota;Animalia;Platyhelminthes;Cestoda;Tetraphyllidea;Unclassified_Tetraphyllidea_(o);Unclassified_Tetraphyllidea_(o)	3	3
Eukaryota;Chloroplastida;Phragmoplastophyta;Embryophyta;Malvales;Malvales_Incertae_sedis;Gossypium	1	1
Eukaryota;Fungi;Basidiomycota;Agaricomycetes;Phallales;Phallaceae;Phallus	1	1
Eukaryota;Chloroplastida;Phragmoplastophyta;Embryophyta;Pinales;Pinales_Incertae_sedis;Pinus	1	1
"""  # noqa: E501


TEST_5_DF_REAL_SAMPLE_CLASS = r"""tax	barcode01	total
Eukaryota;Animalia;Mollusca;Bivalvia	684	684
Unclassified;Unknown;Unknown;Unknown	25	25
Eukaryota;Animalia;Platyhelminthes;Cestoda	3	3
Eukaryota;Chloroplastida;Phragmoplastophyta;Embryophyta	2	2
Eukaryota;Fungi;Basidiomycota;Agaricomycetes	1	1
"""  # noqa: E501


# -------------------------
# TEST 6: case03 of test data, request different ranks
# - Known composition.
# -------------------------
TEST_6_JSON_CASE03 = r"""{
  "reads_perfect": {
    "Bacteria": {
      "rank": "superkingdom",
      "count": 700,
      "children": {
        "Cyanobacteria": {
          "rank": "phylum",
          "count": 200,
          "children": {
            "Cyanobacteriia": {
              "rank": "class",
              "count": 200,
              "children": {
                "Synechococcales": {
                  "rank": "order",
                  "count": 100,
                  "children": {
                    "Cyanobiaceae": {
                      "rank": "family",
                      "count": 100,
                      "children": {
                        "Prochlorococcus MIT9313": {
                          "rank": "genus",
                          "count": 100,
                          "children": {}
                        }
                      }
                    }
                  }
                },
                "Cyanobacteriales": {
                  "rank": "order",
                  "count": 100,
                  "children": {
                    "Microcystaceae": {
                      "rank": "family",
                      "count": 100,
                      "children": {
                        "Synechocystis PCC-6803": {
                          "rank": "genus",
                          "count": 100,
                          "children": {}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "Proteobacteria": {
          "rank": "phylum",
          "count": 500,
          "children": {
            "Gammaproteobacteria": {
              "rank": "class",
              "count": 300,
              "children": {
                "Enterobacterales": {
                  "rank": "order",
                  "count": 300,
                  "children": {
                    "Enterobacteriaceae": {
                      "rank": "family",
                      "count": 100,
                      "children": {
                        "Escherichia-Shigella": {
                          "rank": "genus",
                          "count": 100,
                          "children": {}
                        }
                      }
                    },
                    "Vibrionaceae": {
                      "rank": "family",
                      "count": 200,
                      "children": {
                        "Vibrio": {
                          "rank": "genus",
                          "count": 200,
                          "children": {}
                        }
                      }
                    }
                  }
                }
              }
            },
            "Alphaproteobacteria": {
              "rank": "class",
              "count": 200,
              "children": {
                "Rickettsiales": {
                  "rank": "order",
                  "count": 200,
                  "children": {
                    "Rickettsiaceae": {
                      "rank": "family",
                      "count": 200,
                      "children": {
                        "Rickettsia": {
                          "rank": "genus",
                          "count": 200,
                          "children": {}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "Eukaryota": {
      "rank": "superkingdom",
      "count": 200,
      "children": {
        "Fungi": {
          "rank": "kingdom",
          "count": 200,
          "children": {
            "Ascomycota": {
              "rank": "phylum",
              "count": 100,
              "children": {
                "Saccharomycetes": {
                  "rank": "class",
                  "count": 100,
                  "children": {
                    "Saccharomycetales": {
                      "rank": "order",
                      "count": 100,
                      "children": {
                        "Debaryomycetaceae": {
                          "rank": "family",
                          "count": 100,
                          "children": {
                            "Candida-Lodderomyces clade": {
                              "rank": "genus",
                              "count": 100,
                              "children": {}
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            },
            "Basidiomycota": {
              "rank": "phylum",
              "count": 100,
              "children": {
                "Malasseziomycetes": {
                  "rank": "class",
                  "count": 100,
                  "children": {
                    "Malasseziales": {
                      "rank": "order",
                      "count": 100,
                      "children": {
                        "Malasseziaceae": {
                          "rank": "family",
                          "count": 100,
                          "children": {
                            "Malassezia": {
                              "rank": "genus",
                              "count": 100,
                              "children": {}
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "Archaea": {
      "rank": "superkingdom",
      "count": 200,
      "children": {
        "Euryarchaeota": {
          "rank": "phylum",
          "count": 100,
          "children": {
            "Methanobacteria": {
              "rank": "class",
              "count": 100,
              "children": {
                "Methanobacteriales": {
                  "rank": "order",
                  "count": 100,
                  "children": {
                    "Methanobacteriaceae": {
                      "rank": "family",
                      "count": 100,
                      "children": {
                        "Methanobrevibacter": {
                          "rank": "genus",
                          "count": 100,
                          "children": {}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "Crenarchaeota": {
          "rank": "phylum",
          "count": 100,
          "children": {
            "Thermoprotei": {
              "rank": "class",
              "count": 100,
              "children": {
                "Sulfolobales": {
                  "rank": "order",
                  "count":100,
                  "children": {
                    "Sulfolobaceae": {
                      "rank": "family",
                      "count": 100,
                      "children": {
                        "Sulfolobus": {
                          "rank": "genus",
                          "count": 100,
                          "children": {}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


TEST_6_DF_CASE03_GENUS = r"""tax	reads_perfect	total
Bacteria;Bacteria_none;Proteobacteria;Alphaproteobacteria;Rickettsiales;Rickettsiaceae;Rickettsia	200	200
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Enterobacterales;Vibrionaceae;Vibrio	200	200
Archaea;Archaea_none;Crenarchaeota;Thermoprotei;Sulfolobales;Sulfolobaceae;Sulfolobus	100	100
Bacteria;Bacteria_none;Cyanobacteria;Cyanobacteriia;Cyanobacteriales;Microcystaceae;Synechocystis PCC-6803	100	100
Archaea;Archaea_none;Euryarchaeota;Methanobacteria;Methanobacteriales;Methanobacteriaceae;Methanobrevibacter	100	100
Bacteria;Bacteria_none;Cyanobacteria;Cyanobacteriia;Synechococcales;Cyanobiaceae;Prochlorococcus MIT9313	100	100
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria;Enterobacterales;Enterobacteriaceae;Escherichia-Shigella	100	100
Eukaryota;Fungi;Ascomycota;Saccharomycetes;Saccharomycetales;Debaryomycetaceae;Candida-Lodderomyces clade	100	100
Eukaryota;Fungi;Basidiomycota;Malasseziomycetes;Malasseziales;Malasseziaceae;Malassezia	100	100
"""  # noqa: E501


TEST_6_DF_CASE03_CLASS = r"""tax	reads_perfect	total
Bacteria;Bacteria_none;Proteobacteria;Alphaproteobacteria	200	200
Bacteria;Bacteria_none;Proteobacteria;Gammaproteobacteria	300	300
Archaea;Archaea_none;Crenarchaeota;Thermoprotei	100	100
Bacteria;Bacteria_none;Cyanobacteria;Cyanobacteriia	200	200
Archaea;Archaea_none;Euryarchaeota;Methanobacteria	100	100
Eukaryota;Fungi;Ascomycota;Saccharomycetes	100	100
Eukaryota;Fungi;Basidiomycota;Malasseziomycetes	100	100
"""  # noqa: E501
