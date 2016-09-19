import csv
from os import path
import numpy as np
from numpy import fabs
from scipy.interpolate import RectBivariateSpline,griddata


def overlay(xt,ys,coef):
    a = coef[0]
    b = coef[1]
    c = coef[2]
    d = coef[3]
    e = coef[4]
    f = coef[5]
    g = coef[6]
    h = coef[7]
    i = coef[8]
    j = coef[9]

    return a + b*xt + c*ys + d*xt**2 + e*xt*ys + f*ys**2 + g*xt**3 + h*xt**2*ys + i*xt*ys**2 + j*ys**3


def vorticity(tsr, solidity):
    """
    Using EMG distribution parameters to define the vorticity strength and shape
    
    Parameters
    ----------
    tsr : float
        tip-speed ratio
    solidity : float
        turbine solidity
    
    Returns
    ----------
    loc : array
        array of the location parameter (3 values)
    spr : array
        array of the spread parameter (2 values)
    skw : array
        array of the skew parameter (2 values)
    scl : array
        array of the scale parameter (3 values)
    """
    
    # Reading in csv file (vorticity database)
    basepath = path.join(path.dirname(path.realpath(__file__)), 'data')
    fdata = basepath + path.sep + 'vortdatabase.csv'
    f = open(fdata)
    csv_f = csv.reader(f)
    
    i = 0
    sol_d = np.array([])
    for row in csv_f:
        if i == 0:
            raw = row
            raw = np.delete(raw,0)
            vortdat = raw
            tsr_d = raw # range of tip-speed ratios included
        if row[0] == 'solidity':
            sol_d = np.append(sol_d, float(row[1]))  # range of solidities included
        elif row[0] != 'TSR' and row[0] != 'solidity':
            raw = row
            raw = np.delete(raw,0)
            vortdat = np.vstack([vortdat, raw])  # adding entry to vorticity database array
        i += 1
    f.close()
    
    vortdat = np.delete(vortdat, 0, axis=0) # eliminating first row used as a placeholder
    tsr_d = tsr_d.astype(np.float)  # converting tip-speed ratio entries into floats
    vortdat = vortdat.astype(np.float)  # converting vorticity database entries into floats
    
    # Creating arrays for each EMG parameter
    for i in range(np.size(sol_d)):
        sol = str(i+1)
        
        exec('s'+sol+'_loc1 = vortdat[i*10]\ns'+sol+'_loc2 = vortdat[i*10+1]\ns'+sol+'_loc3 = vortdat[i*10+2]\ns'+sol+'_spr1 = vortdat[i*10+3]\ns'+sol+'_spr2 = vortdat[i*10+4]\ns'+sol+'_skw1 = vortdat[i*10+5]\ns'+sol+'_skw2 = vortdat[i*10+6]\ns'+sol+'_scl1 = vortdat[i*10+7]\ns'+sol+'_scl2 = vortdat[i*10+8]\ns'+sol+'_scl3 = vortdat[i*10+9]\n')
    
    # BIVARIATE SPLINE INTERPOLATION
    
    iz = np.size(sol_d)
    jz = np.size(tsr_d)
    
    # Initializing rectangular matrices
    z_loc1 = np.zeros((iz, jz))
    z_loc2 = np.zeros((iz, jz))
    z_loc3 = np.zeros((iz, jz))
    z_spr1 = np.zeros((iz, jz))
    z_spr2 = np.zeros((iz, jz))
    z_skw1 = np.zeros((iz, jz))
    z_skw2 = np.zeros((iz, jz))
    z_scl1 = np.zeros((iz, jz))
    z_scl2 = np.zeros((iz, jz))
    z_scl3 = np.zeros((iz, jz))
    
    # Transferring raw data into rectangular matrices
    for i in range(iz):
        for j in range(jz):
            sol = str(i+1)
            exec('z_loc1[i, j] = s'+sol+'_loc1[j]')
            exec('z_loc2[i, j] = s'+sol+'_loc2[j]')
            exec('z_loc3[i, j] = s'+sol+'_loc3[j]')
            exec('z_spr1[i, j] = s'+sol+'_spr1[j]')
            exec('z_spr2[i, j] = s'+sol+'_spr2[j]')
            exec('z_skw1[i, j] = s'+sol+'_skw1[j]')
            exec('z_skw2[i, j] = s'+sol+'_skw2[j]')
            exec('z_scl1[i, j] = s'+sol+'_scl1[j]')
            exec('z_scl2[i, j] = s'+sol+'_scl2[j]')
            exec('z_scl3[i, j] = s'+sol+'_scl3[j]')
    
    # Creating a rectangular bivariate spline of the parameter data
    s_loc1 = RectBivariateSpline(sol_d, tsr_d, z_loc1)
    s_loc2 = RectBivariateSpline(sol_d, tsr_d, z_loc2)
    s_loc3 = RectBivariateSpline(sol_d, tsr_d, z_loc3)
    s_spr1 = RectBivariateSpline(sol_d, tsr_d, z_spr1)
    s_spr2 = RectBivariateSpline(sol_d, tsr_d, z_spr2)
    s_skw1 = RectBivariateSpline(sol_d, tsr_d, z_skw1)
    s_skw2 = RectBivariateSpline(sol_d, tsr_d, z_skw2)
    s_scl1 = RectBivariateSpline(sol_d, tsr_d, z_scl1)
    s_scl2 = RectBivariateSpline(sol_d, tsr_d, z_scl2)
    s_scl3 = RectBivariateSpline(sol_d, tsr_d, z_scl3)
    
    # Selecting the specific parameters to use for TSR and solidity
    loc1 = s_loc1(solidity, tsr)
    loc2 = s_loc2(solidity, tsr)
    loc3 = s_loc3(solidity, tsr)
    spr1 = s_spr1(solidity, tsr)
    spr2 = s_spr2(solidity, tsr)
    skw1 = s_skw1(solidity, tsr)
    skw2 = s_skw2(solidity, tsr)
    scl1 = s_scl1(solidity, tsr)
    scl2 = s_scl2(solidity, tsr)
    scl3 = s_scl3(solidity, tsr)
    
    # Creating arrays of the parameters
    loc = np.array([loc1[0, 0], loc2[0, 0], loc3[0, 0]])
    spr = np.array([spr1[0, 0], spr2[0, 0]])
    skw = np.array([skw1[0, 0], skw2[0, 0]])
    scl = np.array([scl1[0, 0], scl2[0, 0], scl3[0, 0]])
    
    return loc, spr, skw, scl

def vorticity2(tsr,solidity):

    #read 4
    coef0 = np.array( [0.0025703809856661534, -0.0007386258659065129, 0.004595508188667984, 0.000380123563204793, -0.0005090098755683027, 0.005744581813281894, -4.103393770815313e-05, -0.0014146918534486358, -0.013975958482495927, 0.0] )
    coef1 = np.array( [-0.5047504670963536, 0.23477391362058556, 0.8414256436198028, -0.04252528528617351, -0.06962875967504166, -0.6566907653208429, 0.002839318332370807, 0.00571803958194812, 0.0070744372783060295, 0.22805286438890995] )
    coef2 = np.array( [0.2878345841026334, 0.11512552658662782, 0.7303949879914625, -0.007035517839387948, -0.18284850673545897, -0.5241921153256568, -0.0003704899921255296, 0.010972527139685873, 0.04380801537377295, 0.1724129349605399] )
    coef3 = np.array( [0.08234816067475287, -0.03530687906626052, -0.3662863944976986, 0.003240141344532779, 0.12172015102204112, 0.2993048183466721, 0.0, -0.009253185586804007, -0.057469126406649716, -0.07257633583877886] )
    coef4 = np.array( [-0.07083579909945328, 0.016182024377569406, 0.1985436342461859, 0.0017738254727425816, -0.09111094817943823, -0.06561408122153217, -0.0005115133402638633, 0.009434288536679505, 0.022392136905926813, 0.0] )
    coef5 = np.array( [-1.6712830849073221, 1.5625053380692426, -6.180392756736983, -0.20407668040293722, -4.6476103643607685, 29.380064536220306, 0.0, 0.7502978877582536, -0.16358232641365608, -19.937609244085568] )
    coef6 = np.array( [-3.423561091777921, -9.228795430171687, 86.95722105482042, 2.772872601988039, -11.968168333741515, -150.61261090270446, -0.24715316589674527, 0.5283723108899993, 4.537286811245538, 82.50581844010263] )
    coef7 = np.array( [-0.19815381951708524, 0.08438758133540872, 1.2650146439483734, -0.007606115512168328, -0.2747023984740461, -0.8844640101378567, 0.0, 0.01870057580949183, 0.0699898278743648, 0.2794360008051127] )
    coef8 = np.array( [2.3932787625531815, -2.020874419612962, -8.938221963838357, 0.576323845480877, 2.8782448498416944, 16.598492450314534, -0.04746016700352029, -0.197101203594028, -1.3860007472886064, -8.289767128060362] )
    coef9 = np.array( [104.40501489600803, -29.942999569370276, -174.42008279158216, 3.708514822202037, 25.14336546356742, 132.35546551746415, -0.16479555172343271, -1.351556690339512, -6.721810844025761, -40.39565289044579] )

    #read 6
    # coef0 = np.array( [0.07709044464625317, -0.04740029165688312, -0.16991048271258233, 0.010185705350301196, 0.06884032150568876, 0.10299017833087143, -0.0007122943215019527, -0.008308822666077508, -0.03435156111077655, 0.0] )
    # coef1 = np.array( [-0.5003717932946304, 0.22610110226599275, 1.3085708132849527, -0.04811681050703861, -0.15715350741292458, -1.2771809638703127, 0.003860117612383805, 0.0128260317514925, 0.07229701122051288, 0.38505299579079794] )
    # coef2 = np.array( [0.18447471588496925, 0.22491446110851412, 0.352882721970498, -0.022220685661704473, -0.26163657606654983, 0.35858243211253543, -0.0002849994734101372, 0.02441732290603862, 0.0017870851288199138, -0.15083295080322173] )
    # coef3 = np.array( [0.07916577329587404, -0.03144757083755946, -0.340832651135764, 0.002728282634468151, 0.10713756080183831, 0.25582398671769246, 0.0, -0.007915289453241086, -0.05011301604845094, -0.044729906209416866] )
    # coef4 = np.array( [-0.08562759918040584, 0.014952261574604832, 0.1043146634725098, 0.0027479619455810732, -0.03298914821394256, 0.014119501371758644, -0.0006302605846889573, 0.004795277656533713, -0.0139277398842217, 0.0] )
    # coef5 = np.array( [-1.655460343720484, 1.7367941271405778, -7.238562586343561, -0.23492155695145236, -4.3949689533986, 32.148612999217015, 0.0, 0.7643482585274446, -0.02223360684222774, -22.812878863992015] )
    # coef6 = np.array( [-7.889402871093269, -7.480765809247869, 81.43536734767329, 2.5259032797143357, -12.91777745115153, -130.9655557181711, -0.2273087970688141, 0.46713593707455003, 3.5290597349608985, 75.13101144264893] )
    # coef7 = np.array( [-0.281860241228644, 0.15337593599273622, 1.3874156400015434, -0.013349346689954193, -0.4499765244970901, -0.6531816298972863, 0.0, 0.030394272428236082, 0.13639777182324817, 0.06777399286119161] )
    # coef8 = np.array( [3.107813107183466, -1.9460558282949345, -15.241180687382021, 0.16298098950801992, 8.55044346091066, 12.09032038574375, 2.9217309255614916e-05, -0.6535225876034279, -3.0377325606705443, -3.523374903798156] )
    # coef9 = np.array( [12531.99583129866, -40.94972927053573, -53958.89757682066, 5.918882881361156, 28.034407867118492, 74594.37812720957, -0.28546799520575034, -2.0428378590399507, -4.530858713114041, -33138.3719592977] )

    #read 4, no turb, simpler
    # coef0 = np.array( [0.06717845209660979, -0.04281287619493822, -0.1529324839882259, 0.0093261084429391, 0.06631815687894657, 0.10883298966349286, -0.0006643986096112645, -0.007407591104142614, -0.0453745113095438, 0.0] )
    # coef1 = np.array( [-0.3556484334113687, 0.17490581813808356, 0.6183155493429843, -0.04224261814483536, 0.02530888226858403, -0.5780843437993584, 0.003626379084238409, -0.0005548038985988851, -9.376027247700653e-05, 0.17276495881085827] )
    # coef2 = np.array( [0.13134518448270638, 0.24037618529391278, 0.8114550118454551, -0.02360077103821555, -0.3734832417780626, -0.2350978780573516, -4.123889795680468e-05, 0.028323639631224595, 0.08739000382454407, 0.005673210297865079] )
    # coef3 = np.array( [0.0668217664365869, -0.02872155158019284, -0.28846909095824813, 0.0030682059744380243, 0.09898325863346044, 0.1795505345338577, 0.0, -0.00786818928574068, -0.048556465263782045, 0.003555385441818797] )
    # coef4 = np.array( [-0.07761083882088762, 0.015586553760206193, 0.22176136213846637, -0.004864262629880156, -0.025062339873042006, -0.19316154476825312, 0.00040764202130965375, 0.0012131720115087093, 0.027767177234229994, 0.0] )
    # coef5 = np.array( [-1.2047145182068772, 1.2964571236743023, -5.00931843359495, -0.18095843325877572, -4.509427779074613, 20.201734312916887, 0.0, 0.9965964268637035, -3.1222447263100577, -5.782693861551185] )
    # coef6 = np.array( [-10.116899420346016, 1.9032579233016627, 73.83277522887003, -0.27553510693510863, -22.40423984591767, -96.1794690160868, 0.0, 1.1126611133364892, 13.61214898571955, 33.310034231678586] )
    # coef7 = np.array( [-0.38506834342382334, 0.17727093784307596, 2.004401075621652, -0.016188032545231993, -0.477874622839923, -1.0335185278924466, 0.0, 0.03424362031735874, 0.08931947169317156, 0.27070788626789377] )
    # coef8 = np.array( [2.343608544671663, -1.4425538228790895, -10.064237139210878, -0.2051852193612712, 6.74133752425321, 9.264763130590213, -4.8715203042110845e-05, 0.274769595587078, -6.431928662024021, 0.0] )
    # coef9 = np.array( [21.312761013113303, 12.309744088916668, -43.56737900971533, 1.5733004140333202, -2.8560964711597485, 370.96265255221743, 0.0, -7.947158459502326, -56.52484017218213, 209.0352169010418] )

    #read 4, no turb
    # coef0 = np.array( [0.070254994184101, -0.044071008639271284, -0.15481305719442282, 0.00943746262916168, 0.06636241376332958, 0.09668578997294902, -0.0006588169464598804, -0.007492341482829989, -0.039756895272774886, 0.0] )
    # coef1 = np.array( [-0.3276428492152728, 0.14252641175656589, 0.7037224419890689, -0.03231522230736618, -0.005924642949775362, -0.6224251128000244, 0.002738782823014699, 0.002115560221690271, -0.000637103341901484, 0.19698912174826128] )
    # coef2 = np.array( [0.13700089615722688, 0.26795874799119596, 0.5962932433540777, -0.034628628287775, -0.3155044060636589, -0.05396495439357894, 0.0010395298593350068, 0.023553350169038388, 0.07492479344472126, -0.06338903639744499] )
    # coef3 = np.array( [0.0714609423630718, -0.029035625190649967, -0.3045675825335908, 0.002891150526815011, 0.09901114521577724, 0.1860999120506174, 0.0, -0.007153978403622879, -0.04925285186203384, 0.007193587550316126] )
    # coef4 = np.array( [-0.09016149619619711, 0.022571711868931536, 0.20515631591104713, -0.005952171134244164, -0.017484040555004646, -0.1611286095099908, 0.00045967822973861803, 0.0005405229072654417, 0.01741258384530518, 0.0] )
    # coef5 = np.array( [-1.238985220743571, 1.3286527899877971, -5.874896483152377, -0.18918825669374859, -4.332925920753639, 22.692011147064864, 0.0, 1.0144776940189615, -3.255605170912164, -8.325646081014945] )
    # coef6 = np.array( [-12.211623763396398, 3.2934621831676836, 82.55414193927649, -0.4257804304840048, -26.439590178967993, -107.74625176382813, 0.0, 1.3779968118759802, 14.84648323859742, 42.83985010504642] )
    # coef7 = np.array( [-0.4516379168031496, 0.25908947039133073, 1.7544027027399942, -0.04063980350050981, -0.36932275557373007, -1.066086917841913, 0.0020551445057048466, 0.02439321357350504, 0.07603039288059049, 0.33848636832790147] )
    # coef8 = np.array( [0.3967484400812946, 0.1150375520075606, -3.498775208155652, -0.22795506461625992, 1.7630789725512368, 3.4505845783779505, -0.0007697052807004763, 0.3189174002014557, -2.647713653044302, 0.8614382847041167] )
    # coef9 = np.array( [97.47894016390093, -34.36434763030853, -46.35164835363673, 0.5467347201651686, 21.28617807604522, 174.745424016113, 0.0, 1.6666161079261155, 4.116569839967451, -209.90084237045315] )


    loc1 = overlay(tsr,solidity,coef0)
    loc2 = overlay(tsr,solidity,coef1)
    loc3 = overlay(tsr,solidity,coef2)
    spr1 = overlay(tsr,solidity,coef3)
    spr2 = overlay(tsr,solidity,coef4)
    skw1 = overlay(tsr,solidity,coef5)
    skw2 = overlay(tsr,solidity,coef6)
    scl1 = overlay(tsr,solidity,coef7)
    scl2 = overlay(tsr,solidity,coef8)
    scl3 = overlay(tsr,solidity,coef9)

    return loc1,loc2,loc3,spr1,spr2,skw1,skw2,scl1,scl2,scl3


def velocity(tsr, solidity):
    """
    Using SMG distribution parameters to define the velocity strength and shape
    
    Parameters
    ----------
    tsr : float
        tip-speed ratio
    solidity : float
        turbine solidity
    
    Returns
    ----------
    men : array
        array of the mean parameter (1 values)
    sdv : array
        array of the standard deviation parameter (4 values)
    rat : array
        array of the rate parameter (1 values)
    wdt : array
        array of the translation parameter (1 values)
    spr : array
        array of the spread parameter (4 values)
    scl : array
        array of the scale parameter (3 values)
    """
    # Reading in csv file (vorticity database)
    basepath = path.join(path.dirname(path.realpath(__file__)), 'data')
    # fdata = basepath + path.sep + 'velodatabase_SMG_surf2_edit.csv'
    fdata = basepath + path.sep + 'velodatabase_SMG_surf4.csv'
    f = open(fdata)
    csv_f = csv.reader(f)
    
    i = 0
    sol_d = np.array([])
    for row in csv_f:
        if i == 0:
            raw = row
            raw = np.delete(raw, 0)
            velodat = raw
            tsr_d = raw # range of tip-speed ratios included
        if row[0] == 'solidity':
            sol_d = np.append(sol_d, float(row[1])) # range of solidities included
        elif row[0] != 'TSR' and row[0] != 'solidity':
            raw = row
            raw = np.delete(raw, 0)
            velodat = np.vstack([velodat, raw]) # adding entry to vorticity database array
        i += 1
    f.close()

    velodat = np.delete(velodat, 0, axis=0) # eliminating first row used as a placeholder
    tsr_d = tsr_d.astype(np.float) # converting tip-speed ratio entries into floats
    velodat = velodat.astype(np.float) # converting vorticity database entries into floats
    
    # Creating arrays for each SMG parameter
    for i in range(np.size(sol_d)):
        sol = str(i+1)
        
        exec('s'+sol+'_men = velodat[i*14]\ns'+sol+'_sdv1 = velodat[i*14+1]\ns'+sol+'_sdv2 = velodat[i*14+2]\ns'+sol+'_sdv3 = velodat[i*14+3]\ns'+sol+'_sdv4 = velodat[i*14+4]\ns'+sol+'_rat = velodat[i*14+5]\ns'+sol+'_wdt = velodat[i*14+6]\ns'+sol+'_spr1 = velodat[i*14+7]\ns'+sol+'_spr2 = velodat[i*14+8]\ns'+sol+'_spr3 = velodat[i*14+9]\ns'+sol+'_spr4 = velodat[i*14+10]\ns'+sol+'_scl1 = velodat[i*14+11]\ns'+sol+'_scl2 = velodat[i*14+12]\ns'+sol+'_scl3 = velodat[i*14+13]\n')

    # NEAREST ND INTERPOLATION

    iz = np.size(sol_d)
    jz = np.size(tsr_d)

    # Transferring parameter arrays to data matrix
    dataset = np.zeros((14*iz,jz))

    for i in range(iz):
        sol = str(i+1)
        exec('dataset[i*14] = s'+sol+'_men')
        exec('dataset[i*14+1] = s'+sol+'_sdv1')
        exec('dataset[i*14+2] = s'+sol+'_sdv2')
        exec('dataset[i*14+3] = s'+sol+'_sdv3')
        exec('dataset[i*14+4] = s'+sol+'_sdv4')
        exec('dataset[i*14+5] = s'+sol+'_rat')
        exec('dataset[i*14+6] = s'+sol+'_wdt')
        exec('dataset[i*14+7] = s'+sol+'_spr1')
        exec('dataset[i*14+8] = s'+sol+'_spr2')
        exec('dataset[i*14+9] = s'+sol+'_spr3')
        exec('dataset[i*14+10] = s'+sol+'_spr4')
        exec('dataset[i*14+11] = s'+sol+'_scl1')
        exec('dataset[i*14+12] = s'+sol+'_scl2')
        exec('dataset[i*14+13] = s'+sol+'_scl3')

    # Transferring data matrix to TSR, soldity, and parameter arrays
    points1 = np.array([])
    points2 = np.array([])
    points3 = np.array([])
    values = np.array([])
    for i in range(jz):
        for j in range(iz):
            for k in range(14):
                points1 = np.append(points1,tsr_d[i])
                points2 = np.append(points2,sol_d[j])
                points3 = np.append(points3,k+1)
                values = np.append(values,dataset[j*14+k,i])

    # Identifying nearest ND point to CFD data set
    met = 'nearest'
    men = griddata((points1,points2,points3),values,(tsr,solidity,1),method=met)
    sdv1 = griddata((points1,points2,points3),values,(tsr,solidity,2),method=met)
    sdv2 = griddata((points1,points2,points3),values,(tsr,solidity,3),method=met)
    sdv3 = griddata((points1,points2,points3),values,(tsr,solidity,4),method=met)
    sdv4 = griddata((points1,points2,points3),values,(tsr,solidity,5),method=met)
    rat = griddata((points1,points2,points3),values,(tsr,solidity,6),method=met)
    wdt = griddata((points1,points2,points3),values,(tsr,solidity,7),method=met)
    spr1 = griddata((points1,points2,points3),values,(tsr,solidity,8),method=met)
    spr2 = griddata((points1,points2,points3),values,(tsr,solidity,9),method=met)
    spr3 = griddata((points1,points2,points3),values,(tsr,solidity,10),method=met)
    spr4 = griddata((points1,points2,points3),values,(tsr,solidity,11),method=met)
    scl1 = griddata((points1,points2,points3),values,(tsr,solidity,12),method=met)
    scl2 = griddata((points1,points2,points3),values,(tsr,solidity,13),method=met)
    scl3 = griddata((points1,points2,points3),values,(tsr,solidity,14),method=met)

    # Identifying nearest TSR and solidity to given variables
    pointst = np.copy(points1)/tsr - 1.
    pointss = np.copy(points2)/solidity - 1.
    ti = np.argmin(fabs(pointst))
    si = np.argmin(fabs(pointss))
    tsrn = points1[ti]
    soln = points2[si]

    # Creating arrays of the parameters
    men = np.array([men])
    sdv = np.array([sdv1, sdv2, sdv3, sdv4])
    rat = np.array([rat])
    wdt = np.array([wdt])
    spr = np.array([spr1, spr2, spr3, spr4])
    scl = np.array([scl1, scl2, scl3])

    return men,sdv,rat,wdt,spr,scl,tsrn,soln


def velocity2(tsr,solidity):
    coef0 = np.array( [69.31120214165799, -14.54226846455916, -182.9484314845766, 0.7757500007593103, 17.077128640459204, 205.7405780507834, 0.0, 0.6952004161258284, -8.656278871516317, -80.30651611713891] )
    coef1 = np.array( [20.796591097382365, -6.244181130387176, -8.587693125209208, 0.8142615941603905, 1.8506138334190578, 0.0, -0.03363107177764374, 0.12223019591467849, 0.0, 0.0] )
    coef2 = np.array( [-0.015294073403020714, 0.020473995751279686, 0.13789844492064895, -0.0052638657413030055, -0.11469080246898106, -0.19707130831185676, 0.00028907835977146215, 0.020435994570160664, 0.12862824866464892, 0.0] )
    coef3 = np.array( [15.938353497212011, -7.420923601227339, -17.81286649008919, 1.2062417608423517, 3.955459751836299, 7.241485498819938, -0.06694101282588388, -0.21226646110737413, -0.7478822202018863, 0.0] )
    coef4 = np.array( [0.2619104899556741, -0.073703248730009, -0.18110278053024495, 0.0, 0.08236981420749905, -0.07033060400290583, 0.0, 0.0, 0.0, 0.0] )
    coef5 = np.array( [1.2772126399139734, -0.28793513736493115, -0.9675440002861441, 0.022232873411874163, 0.16702810476509866, 0.21867217108386947, -1.8776159079600002e-05, -0.004624278672205385, 0.03751786152363546, -0.060347089708739324] )
    coef6 = np.array( [0.07310683619403949, -0.0731078636275017, -0.37932110788073947, 0.017633578369773174, 0.2769037348921203, 0.3208692982952059, -0.0011170884942625948, -0.015307930271091856, -0.08194905828120999, 0.0] )
    coef7 = np.array( [83.62824233391731, -20.14985073380763, -119.3133697945351, 2.186060358249593, 14.877953353208454, 82.12647543800952, -0.08428765888226167, -0.7381718005397198, -3.2357192642279067, -24.477809412902253] )


    coef0 = np.array( [96.78787569603121, -25.958433685317107, -264.69170623326727, 1.87464555787568, 51.87562056487128, 239.2539339088309, 0.0, -2.3683807739615252, -21.77566460245587, -72.16807143827123] )
    coef1 = np.array( [-1.5607308407855849, 3.781810622756087, 3.8589765773806635, -0.7828322617478133, 1.2851127289130426, -0.9780850425505745, 0.053806398646338315, -0.004216458910203603, -1.9029882519009809, 1.1216497213945278] )
    coef2 = np.array( [0.04474980994165066, -0.01781338292690174, -0.2928285095380119, 0.0022556558140634383, 0.05240119175487355, 0.42156882995131023, -0.0001656666942084075, 0.004380334411217462, 0.0017623529889020642, -0.22543995985088924] )
    coef3 = np.array( [0.44456289023552864, -0.15060882084694283, -0.5839444598651449, 0.017653548310866428, 0.13144967434649582, 0.25020074597304015, -0.0006767773859921913, -0.007996991123069315, -0.02796902183745419, -0.031964165183268466] )
    coef4 = np.array( [-2.7247813990305123, 4.724192699399499, 10.36801276589125, -1.2166148524625373, -7.9280796594054115, 0.0, 0.08822977083653992, 0.677747763097038, 0.0, 0.0] )
    coef5 = np.array( [0.7506898031843403, -0.06444761119603926, -0.837579404198149, -0.009267404487624946, 0.19446504777032012, 0.09424648444431204, 0.0013092828164535946, -0.004935762159895988, -0.03629240478785554, 0.20951216903837414] )
    coef6 = np.array( [0.14354129036499289, -0.0713909071063587, -0.6243972531747024, 0.011973080714083267, 0.30933176461872885, 0.6699155214984721, -0.0004766541652853193, -0.018026755908751073, -0.08464726862880464, -0.20627751665213928] )
    coef7 = np.array( [41.295014624752916, -4.660859316203044, -39.90052730458264, 0.19616479682310406, 1.7128905012718616, 13.61901360510989, 0.0, 0.0, 0.0, 0.0] )

    #QME2pow3 (first best)
    coef0 = np.array( [132.6722372610478, -34.93465942596633, -380.4394325386311, 2.4459067170844673, 68.60880512259655, 374.49565996499416, 0.0, -2.631298457155278, -32.41512006231126, -122.91288763921081] )
    coef1 = np.array( [3.2841496359202185, 2.5258185980166776, -19.32475137654605, -0.6635605862665878, 4.39276994866165, 31.457505087283618, 0.05362178673494203, -0.1291054894957141, -3.8167603944580875, -13.111805505269034] )
    coef2 = np.array( [0.16041249254968282, -0.03660737924109727, -1.3324697946077309, 0.0006952312900736275, 0.26518562270588875, 1.8519148426513374, 0.00010378689556150557, -0.00454873844845595, -0.14497362526941746, -0.7847581114747488] )
    coef3 = np.array( [0.5129822083425051, -0.20140014304589243, -0.25138976836980925, 0.02413866231871476, 0.13084332587949254, -0.2927441073541505, -0.0008954524910658225, -0.009407338557251597, -0.011865207041416847, 0.1874098605524512] )
    coef4 = np.array( [-2.260178381037694, 4.148684620712865, 6.231819496294992, -1.1073679523291522, -5.638070571202504, 0.0, 0.07174203727980469, 0.656402421601931, 0.0, 0.0] )
    coef5 = np.array( [1.0333574828116667, -0.18231961505300875, -1.3077494182082738, 0.007527942821932585, 0.271193222135317, 0.6347854281130164, 0.00046651250333707664, -0.00603448454892895, -0.08287667731283102, 0.008341552496059878] )
    coef6 = np.array( [0.06105811054700276, -0.0441101309198774, -0.2765502943108469, 0.009849233044716597, 0.23043914347423136, 0.27613892118545386, -0.0005264583562888652, -0.012695069285973236, -0.05490202811295547, -0.05645025865265032] )
    coef7 = np.array( [39.95802886172504, -4.656227200127483, -37.89948079419315, 0.22772918100271503, 1.337720465366513, 14.171027502911437, 0.0, 0.0, 0.0, 0.0] )

    #QME2pow3 (second best)
    coef0 = np.array( [110.36030047488595, -27.985029641159635, -317.9413884301561, 1.878631951546971, 56.098972269155766, 312.4289628464063, 0.0, -2.0059698573093683, -27.32200171079657, -100.17261139540484] )
    coef1 = np.array( [1.1862973344821859, 3.2913660782457277, -13.343558670695955, -0.6994710704769485, 2.755577535790919, 24.41590484609918, 0.04455378755559768, 0.07032158254873834, -3.7862576950238216, -8.720769026464755] )
    coef2 = np.array( [0.1255751578337351, -0.023873145621841157, -1.1731644110837747, 0.0, 0.21525685130206756, 1.6926888990773763, 0.0, 0.0, -0.13006998640696732, -0.7203847208910938] )
    coef3 = np.array( [0.604604570567267, -0.23669313806774606, -0.34190928626245876, 0.028525238398903852, 0.1626346287030023, -0.3025727427349951, -0.0010750324435612887, -0.011521887892891916, -0.018045156540234433, 0.21032697191920527] )
    coef4 = np.array( [-2.1579735618906395, 3.8231906624406182, 6.203244641496877, -0.9977766045457122, -5.480607527455324, 0.0, 0.06455330726056291, 0.6226831089712495, 0.0, 0.0] )
    coef5 = np.array( [0.9956179768896047, -0.1851658632946506, -1.1667623179247888, 0.010377359343377409, 0.2551128576510571, 0.5398026250286322, 0.0002202373562505837, -0.006404037687646303, -0.07055287805082666, 0.0] )
    coef6 = np.array( [0.042251377261527216, -0.03314023685276692, -0.2132999223735087, 0.007497085100377211, 0.21850016639856837, 0.16869202696085084, -0.0003310698528521071, -0.012647244265627924, -0.04544937719634106, 0.0] )
    coef7 = np.array( [39.34005307348499, -4.563877850653355, -36.29775209491077, 0.215754042224762, 1.3565208067720742, 12.914792852294092, 0.0, 0.0, 0.0, 0.0] )

    #QME2pow3nolowsol- read 4
    coef0 = np.array( [162.01484856971925, -56.609864070990234, -355.70551730073817, 7.441545920384457, 68.27557456737954, 313.6477766176516, -0.36296739887760926, -3.059800644673732, -26.93879800612448, -97.63632023913904] )
    coef1 = np.array( [12.005283701063519, -1.4497683016136294, 2.025888538683516, 0.3451759927458214, -3.4669620392642195, 0.0, -0.03599634973233857, 0.5499946757329268, 0.0, 0.0] )
    coef2 = np.array( [0.12243393220036747, -0.02316760833792499, -1.1276549161424203, 0.0, 0.21520334050736944, 1.5115650445205369, 0.0, 0.0, -0.09527529701598908, -0.6305972412941608] )
    coef3 = np.array( [17.045653733446905, -7.109030611783756, -20.573282296996318, 1.1029296870333236, 3.5695275243841973, 8.974877754198436, -0.06073977359005388, -0.14450038362380763, -0.6945375395480806, 0.0] )
    coef4 = np.array( [0.20839238751853925, -0.05271758336624696, -0.23341087144590228, 0.0, 0.053816859016249385, 0.09460371654696077, 0.0, 0.0, 0.0, 0.0] )
    coef5 = np.array( [2.0613301467592935, -0.7580627960490468, -2.5037883547617543, 0.12286789883083443, 0.47305924471810273, 1.9514944614317928, -0.007013481651929264, -0.019740360759842132, -0.0965527494904921, -0.6511401051886425] )
    coef6 = np.array( [-0.34906334693041674, 0.1642291098179862, 0.7045266184312676, -0.026952864558864264, -0.00790860595329445, -0.7704052427229808, 0.0016460152773705218, 0.0020959758722712205, 0.026084713837892466, 0.3635796133191761] )
    coef7 = np.array( [65.90077003437048, -16.32506271209903, -83.04369062042286, 2.309531241433348, 6.699777361830141, 68.48468652184935, -0.12114862990182561, -0.395871456719106, -0.7045449532610489, -26.030263778257073] )

    #QME2pow3nolowsol- read 6
    # coef0 = np.array( [165.07314104246785, -59.18038687801655, -345.8660615317703, 7.703464930809148, 72.02203499745764, 284.6917729222726, -0.3519392591029661, -3.9143275178899013, -24.12300364594809, -87.91913822082697] )
    # coef1 = np.array( [15.180811389780212, -1.5333398826796132, -3.155799330162729, -0.10364479941326102, -1.4414967446851423, 0.0, 0.014842633579294938, 0.4550939587483728, 0.0, 0.0] )
    # coef2 = np.array( [0.09981515491842988, -0.01805873026820708, -0.8463463663343962, 0.0, 0.15016235647999196, 1.0867182997554259, 0.0, 0.0, -0.018037338744559518, -0.5023748773270023] )
    # coef3 = np.array( [16.581892164055247, -6.719817843308753, -21.09755798045135, 0.9761456751948691, 3.9202297608411483, 9.327067582404787, -0.0499506000040208, -0.15763420825432914, -0.91998095290952, 0.0] )
    # coef4 = np.array( [0.18577215475424189, -0.05161182532367709, -0.20178512174325328, 0.0, 0.06238921790389922, 0.060777782935049304, 0.0, 0.0, 0.0, 0.0] )
    # coef5 = np.array( [1.834096942281506, -0.6399356253855367, -2.8577792696275375, 0.09750537627893253, 0.6048816138224647, 2.6335716210850237, -0.005020302032475107, -0.03327881236854545, -0.1576721083781526, -1.0196564910560306] )
    # coef6 = np.array( [-0.3286827178749495, 0.15764097533789875, 0.6383480473750013, -0.02609212306689949, 0.03131120857064077, -0.7399575804315821, 0.0015007249274216036, 0.00016018805728395348, -0.0028433458843963423, 0.37465303670542127] )
    # coef7 = np.array( [61.97717839578156, -18.245493176697064, -58.242565011591616, 2.946432673365592, 4.052738037033063, 43.31648392779778, -0.15760396961612427, -0.5230517810124309, 1.8401978257876566, -19.242326572824968] )

    spr1 = overlay(tsr,solidity,coef0)
    pow1 = overlay(tsr,solidity,coef1)
    pow2 = overlay(tsr,solidity,coef2)
    spr2 = overlay(tsr,solidity,coef3)
    skw = overlay(tsr,solidity,coef4)
    scl1 = overlay(tsr,solidity,coef5)
    scl2 = overlay(tsr,solidity,coef6)
    scl3 = overlay(tsr,solidity,coef7)

    return spr1,pow1,pow2,spr2,skw,scl1,scl2,scl3