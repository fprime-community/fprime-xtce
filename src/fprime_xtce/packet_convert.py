from .type_converter import convert_identifier

built_ins =[
  {
    "SequenceContainer": {
      "name": "CCSDSPacket",
      "abstract": "true",
      "EntryList": [
        { "ParameterRefEntry": { "parameterRef": "CCSDS_TM_Sc_Id" } },
        { "ParameterRefEntry": { "parameterRef": "CCSDS_TM_Vc_Id" } },
        { "ParameterRefEntry": { "parameterRef": "CCSDS_TM_Other" } },
        { "ParameterRefEntry": { "parameterRef": "CCSDS_Packet_ID" } },
        { "ParameterRefEntry": { "parameterRef": "CCSDS_Packet_Sequence" } },
        { "ParameterRefEntry": { "parameterRef": "CCSDS_Packet_Length" } }
      ]
    }
  },

  {
    "SequenceContainer": {
      "name": "FPrimeTelemetryPacket",
      "abstract": "true",
      "EntryList": [
        { "ParameterRefEntry": { "parameterRef": "DataDescType" } },
        { "ParameterRefEntry": { "parameterRef": "FPrimePacketId" } },
        { "ParameterRefEntry": { "parameterRef": "FPrimeTime" } }
      ],
      "BaseContainer": {
        "containerRef": "CCSDSPacket",
        "RestrictionCriteria": {
          "ComparisonList": [
            {
              "Comparison": {
                "parameterRef": "CCSDS_Packet_ID/Version",
                "value": "0"
              }
            },
            {
              "Comparison": {
                "parameterRef": "CCSDS_Packet_ID/APID",
                "value": "4"
              }
            }
          ]
        }
      }
    }
  },

  {
    "SequenceContainer": {
      "name": "FPrimeEventPacket",
      "abstract": "true",
      "EntryList": [
        { "ParameterRefEntry": { "parameterRef": "DataDescType" } },
        { "ParameterRefEntry": { "parameterRef": "FPrimeEventId" } },
        { "ParameterRefEntry": { "parameterRef": "FPrimeTime" } }
      ],
      "BaseContainer": {
        "containerRef": "CCSDSPacket",
        "RestrictionCriteria": {
          "ComparisonList": [
            {
              "Comparison": {
                "parameterRef": "CCSDS_Packet_ID/Version",
                "value": "0"
              }
            },
            {
              "Comparison": {
                "parameterRef": "CCSDS_Packet_ID/APID",
                "value": "2"
              }
            }
          ]
        }
      }
    }
  }
]

def convert_packet_definitions(packet_list):
    """
    Convert F Prime packet definitions to XTCE SequenceContainer equivalents.
    
    Args:
        packet_list: List of packet definitions
    """
    xtce_containers = built_ins.copy()
    for packet in packet_list:
        name = packet["name"]
        id = packet["id"]
        members = packet["members"]

        container = {
            "SequenceContainer": {
                "name": name,
                "EntryList": [{ "ParameterRefEntry": { "parameterRef": convert_identifier(channel) } } for channel in members],
                "BaseContainer": {
                    "containerRef": "FPrimeTelemetryPacket",
                    "RestrictionCriteria": {
                        "ComparisonList": [
                            {
                                "Comparison": {
                                    "parameterRef": "FPrimePacketId",
                                    "value": f"{id}"
                                }
                            },
                        ]
                    }
                }
            }
        }
        xtce_containers.append(container)
    return xtce_containers
