import math
import sys
import ROOT

def show_overflow(hist):
    """ Show overflow and underflow on a TH1. h/t Josh """

    nbins          = hist.GetNbinsX()
    underflow      = hist.GetBinContent(   0   )
    underflowerror = hist.GetBinError  (   0   )
    overflow       = hist.GetBinContent(nbins+1)
    overflowerror  = hist.GetBinError  (nbins+1)
    firstbin       = hist.GetBinContent(   1   )
    firstbinerror  = hist.GetBinError  (   1   )
    lastbin        = hist.GetBinContent( nbins )
    lastbinerror   = hist.GetBinError  ( nbins )

    if underflow != 0 :
        newcontent = underflow + firstbin
        if firstbin == 0 :
            newerror = underflowerror
        else:
            newerror = math.sqrt( underflowerror * underflowerror + firstbinerror * firstbinerror )
        hist.SetBinContent(1, newcontent)
        hist.SetBinError  (1, newerror)

    if overflow != 0 :
        newcontent = overflow + lastbin
        if lastbin == 0 :
            newerror = overflowerror
        else:
            newerror = math.sqrt( overflowerror * overflowerror + lastbinerror * lastbinerror )
        hist.SetBinContent(nbins, newcontent)
        hist.SetBinError  (nbins, newerror)

def signed_to_int(hexa, bits):

    # handle hex or string
    if isinstance(hexa, str):
        hexa = int(hexa, base=16)

    # convert to binary
    binary = format(hexa, "0"+str(bits)+"b")

    # already positive?
    if binary[0]=="0":
        return int(binary, base=2)

    # invert 0s to 1s and 1s to 0s
    binary = binary.replace("0", "2")
    binary = binary.replace("1", "0")
    binary = binary.replace("2", "1")

    # add 1
    binary  = "0b" + binary
    integer = int(binary, base=2) + 1

    return -1*integer

def int2sfi(integ, bits):
    """ input integer, output binary string """

    if abs(integ) >= pow(2, bits-1):
        print "ERROR: Cant represent signed %i with %i bits" % (integ, bits)
        return 

    if integ >= 0:
        form = "0"+str(bits)+"b"
        return "0b"+format(integ, form)
    else:
        form = "0"+str(bits-1)+"b"
        bin_str = format(abs(integ), form)
        bin_str = bin_str.replace("0", "2")
        bin_str = bin_str.replace("1", "0")
        bin_str = bin_str.replace("2", "1")
        binary  = int(bin_str, base=2) + 1
        return "0b1" + format(binary, form)

def twos_complement(val, bits):
    """compute the 2's compliment of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def progress(time_diff, nprocessed, ntotal):
    nprocessed = float(nprocessed)
    ntotal     = float(ntotal)
    rate = (nprocessed+1)/time_diff
    sys.stdout.write("\r > %6i / %6i | %2i%% | %8.2fHz | %6.1fm elapsed | %6.1fm remaining" % (nprocessed, ntotal,
                                                                                               100*nprocessed/ntotal, rate,
                                                                                               time_diff/60, (ntotal-nprocessed)/(rate*60)))
    sys.stdout.flush()

