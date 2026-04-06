from ctypes import c_uint16

class STUPID:
    """
    Socket Transport Using Packets for Indeterminate Data
    All data is encoded as a string. Data of any length can be encoded, if the
    data is too long, it will need to be split into multiple packets.
    """

    MAX_DATA_SIZE = 8 * pow(2, 20)
    PACKET_SIZE = 1024
    PACKET_DATA_SIZE = 1020

    STR_ENCODE = "utf-8"

    def __init__(self, seg: c_uint16, tseg: c_uint16, data: bytes):
        self.segment: c_uint16 = seg
        self.totalSegments: c_uint16 = tseg
        self.data: bytes = data

    def getSeg(self) -> int:
        """
        Returns the segment number as an int.
        """
        return self.segment.value

    def getTotalSeg(self) -> int:
        """
        Returns the total segments as an int.
        """
        return self.totalSegments.value

    def toBytes(self) -> bytes:
        """
        Turn the STUPID into PACKET_SIZE bytes.
        """
        return b''.join([
            self.segment.value.to_bytes(2),
            self.totalSegments.value.to_bytes(2),
            self.data
            ])

    @staticmethod
    def fromBytes(data: bytes) -> STUPID:
        """
        Takes a list of bytes and turns it into a STUPID object.
        """
        return STUPID(
            c_uint16(int.from_bytes(data[0:2])),
            c_uint16(int.from_bytes(data[2:4])),
            data[4:STUPID.PACKET_SIZE]
        )

    @staticmethod
    def encodeStupid(data: str) -> list[STUPID]:
        """
        Takes a string data and returns a list of STUPIDs containing the data,
        ready to be send over sockets.
        """
        dataB = data.encode(STUPID.STR_ENCODE)
        strByteLength: int = len(dataB) + 1
        if strByteLength > STUPID.MAX_DATA_SIZE:
            raise Exception("TOO MUCH DATA (over 8MiB)")
        
        numOfPackets: c_uint16 = c_uint16(int(strByteLength / STUPID.PACKET_DATA_SIZE) + 1)

        packetList: list[STUPID] = []

        for i in range(numOfPackets.value):
            packetList.append(
                STUPID(
                    seg  = c_uint16(i),
                    tseg = numOfPackets,
                    data = dataB[i * STUPID.PACKET_DATA_SIZE : (i + 1) * STUPID.PACKET_DATA_SIZE]
                )
            )
        
        return packetList
    
    @staticmethod
    def decodeStupid(packets: list[STUPID]) -> str:
        rstr: str = ""
        for p in packets:
            rstr += p.data.decode(STUPID.STR_ENCODE)
        return rstr












