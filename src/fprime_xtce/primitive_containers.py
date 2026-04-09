""" Contains primitive (built-in) container definitions

This file provides built-in container definitions for primitive containers needed by the XTCE system.

Copyright (c) 2026 LeStarch. All rights reserved.

This software is Licensed under the Apache 2.0 License. See LICENSE for details.
"""
BASE_CONTAINERS = [
    {
        "SequenceContainer": {
            "name": "CCSDSSpacePacket",
            "abstract": "true",
            "EntryList": [
                {"ParameterRefEntry": {"parameterRef": "CCSDS_Packet_ID"}},
                {"ParameterRefEntry": {"parameterRef": "CCSDS_Packet_Sequence"}},
                {"ParameterRefEntry": {"parameterRef": "CCSDS_Packet_Length"}},
            ],
        }
    },
    {
        "SequenceContainer": {
            "name": "FPrimeTelemetryPacket",
            "abstract": "true",
            "EntryList": [
                {"ParameterRefEntry": {"parameterRef": "DataDescType"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimePacketId"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeTime"}},
            ],
            "BaseContainer": {
                "containerRef": "CCSDSSpacePacket",
                "RestrictionCriteria": {
                    "ComparisonList": [
                        {
                            "Comparison": {
                                "parameterRef": "CCSDS_Packet_ID/Version",
                                "value": "0",
                            }
                        },
                        {
                            "Comparison": {
                                "parameterRef": "CCSDS_Packet_ID/APID",
                                "value": "4",
                            }
                        },
                    ]
                },
            },
        }
    },
    {
        "SequenceContainer": {
            "name": "FPrimeTelemetryChannel",
            "abstract": "true",
            "EntryList": [
                {"ParameterRefEntry": {"parameterRef": "DataDescType"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeChannelId"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeTime"}},
            ],
            "BaseContainer": {
                "containerRef": "CCSDSSpacePacket",
                "RestrictionCriteria": {
                    "ComparisonList": [
                        {
                            "Comparison": {
                                "parameterRef": "CCSDS_Packet_ID/Version",
                                "value": "0",
                            }
                        },
                        {
                            "Comparison": {
                                "parameterRef": "CCSDS_Packet_ID/APID",
                                "value": "1",
                            }
                        },
                    ]
                },
            },
        }
    },
    {
        "SequenceContainer": {
            "name": "FPrimeEvent",
            "abstract": "true",
            "EntryList": [
                {"ParameterRefEntry": {"parameterRef": "DataDescType"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeEventId"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeTime"}},
            ],
            "BaseContainer": {
                "containerRef": "CCSDSSpacePacket",
                "RestrictionCriteria": {
                    "ComparisonList": [
                        {
                            "Comparison": {
                                "parameterRef": "CCSDS_Packet_ID/Version",
                                "value": "0",
                            }
                        },
                        {
                            "Comparison": {
                                "parameterRef": "CCSDS_Packet_ID/APID",
                                "value": "2",
                            }
                        },
                    ]
                },
            },
        }
    },
    # ------------------------------------------------------------
    # Fw::FilePacket containers (file APID = 3 = FW_PACKET_FILE)
    # ------------------------------------------------------------
    #
    # Abstract base: parses the F´ ComPacket descriptor (DataDescType, U16)
    # followed by Fw::FilePacket::Header (U8 type + U32 sequenceIndex).
    #
    # Wire format reference: lib/fprime/Fw/FilePacket/FilePacket.hpp.
    # The U16 ComPacket descriptor prefix is added by FileDownlink in
    # lib/fprime/Svc/FileDownlink/FileDownlink.cpp::readPacket_start() /
    # ::readPacket_data() / ::finishHelper() — it is NOT part of the
    # Fw::FilePacket struct itself.
    {
        "SequenceContainer": {
            "name": "FPrimeFilePacket",
            "abstract": "true",
            "EntryList": [
                {"ParameterRefEntry": {"parameterRef": "DataDescType"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeFilePacketType"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeFilePacketSeqIndex"}},
            ],
            "BaseContainer": {
                "containerRef": "CCSDSSpacePacket",
                "RestrictionCriteria": {
                    "ComparisonList": [
                        {
                            "Comparison": {
                                "parameterRef": "CCSDS_Packet_ID/Version",
                                "value": "0",
                            }
                        },
                        {
                            "Comparison": {
                                "parameterRef": "CCSDS_Packet_ID/APID",
                                "value": "3",
                            }
                        },
                    ]
                },
            },
        }
    },
    # Concrete subcontainers: gated on the U8 Fw::FilePacket::Type
    # discriminator value defined in FilePacket.hpp:40.
    #   T_START = 0, T_DATA = 1, T_END = 2, T_CANCEL = 3
    {
        "SequenceContainer": {
            "name": "FPrimeFilePacketStart",
            "EntryList": [
                {"ParameterRefEntry": {"parameterRef": "FPrimeFilePacketFileSize"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeFilePacketSourcePath"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeFilePacketDestinationPath"}},
            ],
            "BaseContainer": {
                "containerRef": "FPrimeFilePacket",
                "RestrictionCriteria": {
                    "ComparisonList": [
                        {
                            "Comparison": {
                                "parameterRef": "FPrimeFilePacketType",
                                "value": "0",
                            }
                        },
                    ]
                },
            },
        }
    },
    {
        "SequenceContainer": {
            "name": "FPrimeFilePacketData",
            "EntryList": [
                {"ParameterRefEntry": {"parameterRef": "FPrimeFilePacketByteOffset"}},
                {"ParameterRefEntry": {"parameterRef": "FPrimeFilePacketDataSize"}},
                # Payload bytes follow but are intentionally not modeled
                # as a parameter; they are consumed by downstream code
                # (e.g. a YAMCS service) directly from the raw stream.
            ],
            "BaseContainer": {
                "containerRef": "FPrimeFilePacket",
                "RestrictionCriteria": {
                    "ComparisonList": [
                        {
                            "Comparison": {
                                "parameterRef": "FPrimeFilePacketType",
                                "value": "1",
                            }
                        },
                    ]
                },
            },
        }
    },
    {
        "SequenceContainer": {
            "name": "FPrimeFilePacketEnd",
            "EntryList": [
                {"ParameterRefEntry": {"parameterRef": "FPrimeFilePacketChecksum"}},
            ],
            "BaseContainer": {
                "containerRef": "FPrimeFilePacket",
                "RestrictionCriteria": {
                    "ComparisonList": [
                        {
                            "Comparison": {
                                "parameterRef": "FPrimeFilePacketType",
                                "value": "2",
                            }
                        },
                    ]
                },
            },
        }
    },
    {
        "SequenceContainer": {
            "name": "FPrimeFilePacketCancel",
            "EntryList": [],
            "BaseContainer": {
                "containerRef": "FPrimeFilePacket",
                "RestrictionCriteria": {
                    "ComparisonList": [
                        {
                            "Comparison": {
                                "parameterRef": "FPrimeFilePacketType",
                                "value": "3",
                            }
                        },
                    ]
                },
            },
        }
    },
]

BASE_COMMANDS = [
    {
        "MetaCommand": {
            "name": "CCSDSPacket",
            "abstract": "true",
            "ArgumentList": [
                {
                    "Argument": {
                        "name": "CCSDS_Version",
                        "argumentTypeRef": "CCSDS_Version_Type",
                    }
                },
                {
                    "Argument": {
                        "name": "CCSDS_Type",
                        "argumentTypeRef": "CCSDS_Type_Type",
                    }
                },
                {
                    "Argument": {
                        "name": "CCSDS_Sec_Hdr_Flag",
                        "argumentTypeRef": "CCSDS_Sec_Hdr_Flag_Type",
                    }
                },
                {
                    "Argument": {
                        "name": "CCSDS_APID",
                        "argumentTypeRef": "CCSDS_APID_Type",
                    }
                },
                {
                    "Argument": {
                        "name": "CCSDS_Group_Flags",
                        "argumentTypeRef": "CCSDS_Group_Flags_Type",
                    }
                },
            ],
            "CommandContainer": {
                "name": "CCSDSPacket",
                "EntryList": [
                    {"ArgumentRefEntry": {"argumentRef": "CCSDS_Version"}},
                    {"ArgumentRefEntry": {"argumentRef": "CCSDS_Type"}},
                    {"ArgumentRefEntry": {"argumentRef": "CCSDS_Sec_Hdr_Flag"}},
                    {"ArgumentRefEntry": {"argumentRef": "CCSDS_APID"}},
                    {"ArgumentRefEntry": {"argumentRef": "CCSDS_Group_Flags"}},
                    {
                        "FixedValueEntry": {
                            "name": "CCSDS_Source_Sequence_Count",
                            "binaryValue": "0000",
                            "sizeInBits": "14",
                        }
                    },
                    {
                        "FixedValueEntry": {
                            "name": "CCSDS_Packet_Length",
                            "binaryValue": "0000",
                            "sizeInBits": "16",
                        }
                    },
                ],
            },
        }
    },
    {
        "MetaCommand": {
            "name": "FPrimeCommand",
            "abstract": "true",
            "BaseMetaCommand": {
                "metaCommandRef": "CCSDSPacket",
                "ArgumentAssignmentList": [
                    {
                        "ArgumentAssignment": {
                            "argumentName": "CCSDS_Version",
                            "argumentValue": "0",
                        }
                    },
                    {
                        "ArgumentAssignment": {
                            "argumentName": "CCSDS_Type",
                            "argumentValue": "TC",
                        }
                    },
                    {
                        "ArgumentAssignment": {
                            "argumentName": "CCSDS_Sec_Hdr_Flag",
                            "argumentValue": "NotPresent",
                        }
                    },
                    {
                        "ArgumentAssignment": {
                            "argumentName": "CCSDS_APID",
                            "argumentValue": "0",
                        }
                    },
                    {
                        "ArgumentAssignment": {
                            "argumentName": "CCSDS_Group_Flags",
                            "argumentValue": "Standalone",
                        }
                    },
                ],
            },
            "ArgumentList": [
                {
                    "Argument": {
                        "name": "OpCode",
                        "argumentTypeRef": "FwOpcodeType",
                    }
                },
            ],
            "CommandContainer": {
                "name": "FPrimeCommand",
                "EntryList": [
                    {
                        "FixedValueEntry": {
                            "name": "Fprime_FW_PACKET_COMMAND",
                            "binaryValue": "0000",
                            "sizeInBits": "16",
                        }
                    },
                    {
                        "ArgumentRefEntry": {
                            "argumentRef": "OpCode",
                      }
                    }
                ],
                "BaseContainer": {"containerRef": "CCSDSPacket"},
            },
        }
    },
]
