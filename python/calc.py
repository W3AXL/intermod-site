from distutils.command.config import config
import json
from re import RegexFlag
import intermod_library.intermod_library as il
import logging

cfg = None

version = "0.1"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger("intermod-calc")

def loadCfg():
    global cfg
    logger.info("Loading config.json")
    cfg = json.load(open('config.json'))

def calcIM():
    txChanTable = cfg['tx-frequencies']
    rxChanTable = cfg['rx-frequencies']
    # Get first column for TX frequencies
    txFreqs = [i[0] for i in txChanTable]
    # Get second column for TX bandwidths
    txBws = [i[1] for i in txChanTable]
    # Get first column for RX frequencies
    rxFreqs = [i[0] for i in rxChanTable]
    # Get second column for RX bandwidths
    rxBws = [i[1] for i in rxChanTable]
    # Get order
    order = cfg['order']
    # Debug print
    logger.info("Loaded TX frequencies for calculation: {}".format(txFreqs))
    logger.info("Loaded RX frequencies for calculation: {}".format(rxFreqs))
    # Calculate intermod
    table = il.intermod_table(txFreqs, order, order, txBws)
    logger.debug(table)
    # Check for Conflicts
    found = False
    for idx,val in table.iterrows():
        # Get frequency
        freq = val['Frequency']
        order = val['Order']
        bw = val['bandwidth']
        fLow = freq - bw
        fHigh = freq + bw
        # Check if it's a direct hit
        if freq in rxFreqs:
            found = True
            # find what freqs combined
            imFreqs = []
            for txFreqIdx, imProd in enumerate(val[1:-2]):
                if imProd != 0:
                    imFreqs.append(imProd * txFreqs[txFreqIdx])
            # print
            logger.warning("TX IMD {} (order {}) product is on RX frequency!".format(freq, order))
            logger.warning("    -> Products: {}".format(imFreqs))
        # Check if it's within the BW
        for idx, rxFreq in enumerate(rxFreqs):
            # Skip direct overlap
            if freq - rxFreq == 0:
                continue
            # Get ranges for RX freq
            rxBw = rxBws[idx]
            rxLow = rxFreq - rxBw
            rxHigh = rxFreq + rxBw
            # Check for overlap
            if rxLow <= fHigh and fLow <= rxHigh:
                logger.warning("TX IMD {} (order {}, bw {}) is within RX band of frequency {} (bw {})".format(freq, order, bw, rxFreq, rxBw))
                found = True

    if not found:
        logger.info("No TX/RX IMD conflicts found!")

if __name__ == "__main__":
    logger.info("Intermod calculator version {} by W3AXL".format(version))
    loadCfg()
    calcIM()