# MuonSpectrometer/MuonG4/NSW_Sim/trunk/data/stations.v1.74.xml [mm]
NSW_MM_LM1_InnerRadius = 923
NSW_MM_LM1_Length      = 2310
NSW_MM_LM1_outerRadius = NSW_MM_LM1_InnerRadius + NSW_MM_LM1_Length
NSW_MM_LMGap_Length    = 5
NSW_MM_LM2_InnerRadius = NSW_MM_LM1_outerRadius + NSW_MM_LMGap_Length
NSW_MM_LM2_Length      = 1410
NSW_MM_LM2_outerRadius = NSW_MM_LM2_InnerRadius + NSW_MM_LM2_Length
NSW_MM_LM1_baseWidth   = 640.0
NSW_MM_LM1_topWidth    = 2008.5
NSW_MM_LM2_baseWidth   = 2022.8
NSW_MM_LM2_topWidth    = 2220.0

NSW_MM_SM1_InnerRadius  = 895
NSW_MM_SM1_Length       = 2210
NSW_MM_SM1_outerRadius  = NSW_MM_SM1_InnerRadius+NSW_MM_SM1_Length
NSW_MM_SMGap_Length     = 5
NSW_MM_SM2_InnerRadius  = NSW_MM_SM1_outerRadius+NSW_MM_SMGap_Length
NSW_MM_SM2_Length       = 1350
NSW_MM_SM2_outerRadius  = NSW_MM_SM2_InnerRadius+NSW_MM_SM2_Length
NSW_MM_SM1_baseWidth    = 500
NSW_MM_SM1_topWidth     = 1319.2
NSW_MM_SM2_baseWidth    = 1321.1
NSW_MM_SM2_topWidth     = 1821.5

class Trapezoid(object):
    def __init__(self, name):
        if name == "LM1":
            self.inner_radius = NSW_MM_LM1_InnerRadius
            self.outer_radius = NSW_MM_LM1_outerRadius
            self.length       = NSW_MM_LM1_Length
            self.base_width   = NSW_MM_LM1_baseWidth
            self.top_width    = NSW_MM_LM1_topWidth
        elif name == "LM2":
            self.inner_radius = NSW_MM_LM2_InnerRadius
            self.outer_radius = NSW_MM_LM2_outerRadius
            self.length       = NSW_MM_LM2_Length
            self.base_width   = NSW_MM_LM2_baseWidth
            self.top_width    = NSW_MM_LM2_topWidth
        elif name == "SM1":
            self.inner_radius = NSW_MM_SM1_InnerRadius
            self.outer_radius = NSW_MM_SM1_outerRadius
            self.length       = NSW_MM_SM1_Length
            self.base_width   = NSW_MM_SM1_baseWidth
            self.top_width    = NSW_MM_SM1_topWidth
        elif name == "SM2":
            self.inner_radius = NSW_MM_SM2_InnerRadius
            self.outer_radius = NSW_MM_SM2_outerRadius
            self.length       = NSW_MM_SM2_Length
            self.base_width   = NSW_MM_SM2_baseWidth
            self.top_width    = NSW_MM_SM2_topWidth
        else:
            self.fatal("Need trapezoid to be LM1, LM2, SM1, or SM2!")

    def outside_boundary(self, x, y):

        # equations for the left/right boundaries of the trapezoid
        slope  = (self.outer_radius - self.inner_radius) / ((self.top_width - self.base_width) / 2.0)
        offset = self.inner_radius - (slope * self.base_width / 2.0)

        if y > self.outer_radius     : return True # top
        if y < self.inner_radius     : return True # bottom
        if x >  (y - offset) / slope : return True # right
        if x < -(y - offset) / slope : return True # left

    def inside_boundary(self, x, y):
        return not self.outside_boundary(x, y)


def fatal(message):
    import sys
    sys.exit("Error in %s: %s" % (__file__, message))

        
