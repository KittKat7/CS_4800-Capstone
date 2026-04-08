
class STUPID:
    """
    Socket Transport Using Packets for Indeterminate Data
    All data is encoded as a string. Data of any length can be encoded, if the
    data is too long, it will need to be split into multiple packets.
    """

    LEN_BYTES:        int = 2
    MAX_DATA_SIZE:    int = 8 * pow(2, 20)
    PACKET_SIZE:      int = 1024
    PACKET_DATA_SIZE: int = 1018

    STR_ENCODE = "utf-8"

    def __init__(self, lng: int, seg: int, tseg: int, data: bytes):
        self.length: int = lng
        self.segment: int = seg
        self.totalSegments: int = tseg
        self.data: bytes = data

    def getSeg(self) -> int:
        """
        Returns the segment number as an int.
        """
        return self.segment

    def getLastSeg(self) -> int:
        """
        Returns the total segments as an int.
        """
        return self.totalSegments - 1

    def isLastSeg(self) -> bool:
        """
        Returns true if this is the last segment.
        """
        return self.segment == self.totalSegments - 1

    def toBytes(self) -> bytes:
        """
        Turn the STUPID into PACKET_SIZE bytes.
        """
        return b''.join([
            self.length.to_bytes(2),
            self.segment.to_bytes(2),
            self.totalSegments.to_bytes(2),
            self.data
        ])


    @staticmethod
    def fromBytes(data: bytes) -> STUPID:
        """
        Takes a list of bytes and turns it into a STUPID object.
        """
        length = int.from_bytes(data[0:2])
        return STUPID(
            length,
            int.from_bytes(data[2:4]),
            int.from_bytes(data[4:6]),
            data[6:length]
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
        
        numOfPackets: int = int(int(strByteLength / STUPID.PACKET_DATA_SIZE) + 1)

        packetList: list[STUPID] = []

        for i in range(numOfPackets):
            pdata = dataB[i * STUPID.PACKET_DATA_SIZE : (i + 1) * STUPID.PACKET_DATA_SIZE]
            packetList.append(
                STUPID(
                    lng  = int(len(pdata) + 6),
                    seg  = int(i),
                    tseg = numOfPackets,
                    data = pdata
                )
            )
        
        return packetList
    
    @staticmethod
    def decodeStupid(packets: list[STUPID]) -> str:
        rstr: str = ""
        for p in packets:
            rstr += p.data.decode(STUPID.STR_ENCODE)
        return rstr












