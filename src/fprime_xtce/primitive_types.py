"""Primitive (built-in) types for XTCE generation

This file contains a set of primitive types that represent the foundation of XTCE type system that are not
(necessarily) derived from the F Prime dictionary.

:author: LeStarch

Copyright (c) 2026 LeStarch. All rights reserved.

This software is Licensed under the Apache 2.0 License. See LICENSE for details.
"""

BASE_FPRIME_TYPES = [
    {
        "IntegerParameterType": {
            "name": "U8",
            "signed":  False,
            "sizeInBits": 8,
            "IntegerDataEncoding": {"encoding": "unsigned", "sizeInBits": 8, "byteOrder": "mostSignificantByteFirst"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "U16",
            "signed":  False,
            "sizeInBits": 16,
            "IntegerDataEncoding": {"encoding": "unsigned", "sizeInBits": 16, "byteOrder": "mostSignificantByteFirst"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "U32",
            "signed":  False,
            "sizeInBits": 32,
            "IntegerDataEncoding": {"encoding": "unsigned", "sizeInBits": 32, "byteOrder": "mostSignificantByteFirst"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "U64",
            "signed":  False,
            "sizeInBits": 64,
            "IntegerDataEncoding": {"encoding": "unsigned", "sizeInBits": 64, "byteOrder": "mostSignificantByteFirst"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "char",
            "signed":  True,
            "sizeInBits": 8,
            "IntegerDataEncoding": {"encoding": "twosComplement", "sizeInBits": 8, "byteOrder": "mostSignificantByteFirst"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "I8",
            "signed":  True,
            "sizeInBits": 8,
            "IntegerDataEncoding": {"encoding": "twosComplement", "sizeInBits": 8, "byteOrder": "mostSignificantByteFirst"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "I16",
            "signed":  True,
            "sizeInBits": 16,
            "IntegerDataEncoding": {"encoding": "twosComplement", "sizeInBits": 16, "byteOrder": "mostSignificantByteFirst"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "I32",
            "signed":  True,
            "sizeInBits": 32,
            "IntegerDataEncoding": {"encoding": "twosComplement", "sizeInBits": 32, "byteOrder": "mostSignificantByteFirst"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "I64",
            "signed":  True,
            "sizeInBits": 64,
            "IntegerDataEncoding": {"encoding": "twosComplement", "sizeInBits": 64, "byteOrder": "mostSignificantByteFirst"},
        }
    },
    {
        "BooleanParameterType": {
            "name": "bool",
            "oneStringValue": "True",
            "zeroStringValue": "False",
            "IntegerDataEncoding": {
                "sizeInBits": 8,
                "encoding": "unsigned",
                "byteOrder": "mostSignificantByteFirst",
            },
        }
    },
    {
        "FloatParameterType": {
            "name": "F32",
            "sizeInBits": 32,
            "FloatDataEncoding": {"sizeInBits": 32, "encoding": "IEEE754_1985", "byteOrder": "mostSignificantByteFirst"},
        },
    },
    {
        "FloatParameterType": {
            "name": "F64",
            "sizeInBits": 64,
            "FloatDataEncoding": {"sizeInBits": 64, "encoding": "IEEE754_1985", "byteOrder": "mostSignificantByteFirst"},
        },
    },
    # Fw::FilePacket::PathName: U8 length prefix + ASCII chars (max 255 bytes).
    # Distinct from F´'s general string type (which uses a U16 length prefix).
    # See lib/fprime/Fw/FilePacket/PathName.cpp.
    {
        "StringParameterType": {
            "name": "FPrimeFilePathType",
            "StringDataEncoding": {
                "encoding": "UTF-8",
                "Variable": {
                    "maxSizeInBits": 255 * 8,
                    "DynamicValue": {
                        "ParameterInstanceRef": {"parameterRef": "_yamcs_ignore"},
                    },
                    "LeadingSize": {"sizeInBitsOfSizeTag": 8},
                },
            },
        },
    },
]

SPACE_PACKET_TYPES = [
    {
        "AggregateParameterType": {
            "name": "CCSDS_Packet_ID_Type",
            "MemberList": [
                {"Member": {"name": "Version", "typeRef": "CCSDS_Version_Type"}},
                {"Member": {"name": "Type", "typeRef": "CCSDS_Type_Type"}},
                {
                    "Member": {
                        "name": "SecHdrFlag",
                        "typeRef": "CCSDS_Sec_Hdr_Flag_Type",
                    }
                },
                {"Member": {"name": "APID", "typeRef": "CCSDS_APID_Type"}},
            ],
        }
    },
    {
        "IntegerParameterType": {
            "name": "CCSDS_Version_Type",
            "signed": "false",
            "UnitSet": {},
            "IntegerDataEncoding": {"sizeInBits": "3"},
        }
    },
    {
        "BooleanParameterType": {
            "name": "CCSDS_Type_Type",
            "zeroStringValue": "TM",
            "oneStringValue": "TC",
            "UnitSet": {},
            "IntegerDataEncoding": {"sizeInBits": "1"},
        }
    },
    {
        "BooleanParameterType": {
            "name": "CCSDS_Sec_Hdr_Flag_Type",
            "zeroStringValue": "NotPresent",
            "oneStringValue": "Present",
            "UnitSet": {},
            "IntegerDataEncoding": {"sizeInBits": "1"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "CCSDS_APID_Type",
            "signed": "false",
            "UnitSet": {},
            "IntegerDataEncoding": {"sizeInBits": "11"},
        }
    },
    {
        "AggregateParameterType": {
            "name": "CCSDS_Packet_Sequence_Type",
            "MemberList": [
                {"Member": {"name": "GroupFlags", "typeRef": "CCSDS_Group_Flags_Type"}},
                {
                    "Member": {
                        "name": "Count",
                        "typeRef": "CCSDS_Source_Sequence_Count_Type",
                    }
                },
            ],
        }
    },
    {
        "EnumeratedParameterType": {
            "name": "CCSDS_Group_Flags_Type",
            "UnitSet": {},
            "IntegerDataEncoding": {"sizeInBits": "2"},
            "EnumerationList": [
                {"Enumeration": {"value": "0", "label": "Continuation"}},
                {"Enumeration": {"value": "1", "label": "First"}},
                {"Enumeration": {"value": "2", "label": "Last"}},
                {"Enumeration": {"value": "3", "label": "Standalone"}},
            ],
        }
    },
    {
        "IntegerParameterType": {
            "name": "CCSDS_Source_Sequence_Count_Type",
            "signed": "false",
            "UnitSet": {},
            "IntegerDataEncoding": {"sizeInBits": "14"},
        }
    },
    {
        "IntegerParameterType": {
            "name": "CCSDS_Packet_Length_Type",
            "signed": "false",
            "UnitSet": {
                "Unit": {
                    "description": "Size",
                }
            },
            "IntegerDataEncoding": {"sizeInBits": "16"},
        }
    }
]

BASE_PARAMETERS = [
    {"Parameter": { "name": "FPrimePacketId",        "parameterTypeRef": "FwTlmPacketizeIdType" }},
    {"Parameter": { "name": "FPrimeEventId",         "parameterTypeRef": "U32" }},
    {"Parameter": { "name": "FPrimeChannelId",       "parameterTypeRef": "U32" }},
    {"Parameter": { "name": "FPrimeTime",            "parameterTypeRef": "Fw/TimeValue" }},
    {"Parameter": { "name": "DataDescType",          "parameterTypeRef": "U16" }},
    {"Parameter": { "name": "CCSDS_Packet_ID",       "parameterTypeRef": "CCSDS_Packet_ID_Type" }},
    {"Parameter": { "name": "CCSDS_Packet_Sequence", "parameterTypeRef": "CCSDS_Packet_Sequence_Type" }},
    {"Parameter": { "name": "CCSDS_Packet_Length",   "parameterTypeRef": "CCSDS_Packet_Length_Type" }},
    # Fw::FilePacket parameters (file APID = 3 = FW_PACKET_FILE).
    # See lib/fprime/Fw/FilePacket/FilePacket.hpp for the wire format.
    {"Parameter": { "name": "FPrimeFilePacketType",            "parameterTypeRef": "U8" }},
    {"Parameter": { "name": "FPrimeFilePacketSeqIndex",        "parameterTypeRef": "U32" }},
    {"Parameter": { "name": "FPrimeFilePacketFileSize",        "parameterTypeRef": "U32" }},
    {"Parameter": { "name": "FPrimeFilePacketByteOffset",      "parameterTypeRef": "U32" }},
    {"Parameter": { "name": "FPrimeFilePacketDataSize",        "parameterTypeRef": "U16" }},
    {"Parameter": { "name": "FPrimeFilePacketChecksum",        "parameterTypeRef": "U32" }},
    {"Parameter": { "name": "FPrimeFilePacketSourcePath",      "parameterTypeRef": "FPrimeFilePathType" }},
    {"Parameter": { "name": "FPrimeFilePacketDestinationPath", "parameterTypeRef": "FPrimeFilePathType" }},
]
