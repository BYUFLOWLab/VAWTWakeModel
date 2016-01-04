"""
Redcued-Order VAWT Wake Model using CFD vorticity data
Developed by Eric Tingey at Brigham Young University

This code models the wake behind a vertical-axis wind turbine based on
parameters like tip-speed ratio, solidity and wind speed by converting the
vorticity of the wake into velocity information. The model uses CFD data
obtained from STAR-CCM+ of simulated turbines to make the wake model as
accurate as possible.

Only valid for tip-speed ratios between 2.5 and 7.0 and solidities between
0.15 and 1.0. Reynolds numbers should also be around the range of 200,000 to
6,000,000.

In this code, up and down are sides of the wake according to:

--------------->-------------------------------------------------
--------------->------<-ROTATION-<------------UP-----------------
--------------->---------=====--------#################----------
--------------->------//       \\#############################---
-FREE-STREAM--->-----|| TURBINE ||########## WAKE ###############
----WIND------->-----||         ||###############################
--------------->------\\       //#############################---
--------------->---------=====--------#################----------
--------------->------>-ROTATION->-----------DOWN----------------
--------------->-------------------------------------------------
"""


import numpy as np
import matplotlib.pyplot as plt
from numpy import pi
from scipy.integrate import dblquad
from scipy.interpolate import RectBivariateSpline

import _vortrun

# from matplotlib import rcParams
# rcParams['font.family'] = 'Times New Roman'


## Vortex Strength
def vorticity(tsr,solidity):
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
    
    tsr_d = np.linspace(2.50,7.0,19) # range of TSRs included
    sol_d = np.array([0.15,0.25,0.5,0.75,1.0]) # range of solidities included

    s1_loc1 = np.array( [-6.562630750395147e-05, -0.00017191227320610046, -0.0002315094856562322, -0.0004058727333861047, -0.0005661835882529029, -0.0008320440400055491, -0.0010323382990923104, -0.0013344876809095077, -0.001705777885855754, -0.002174619194481279, -0.0027754071417600045, -0.003239573959024916, -0.003838401966633193, -0.004489699887257399, -0.004989334935379721, -0.006335219454824018, -0.007009988095005731, -0.007280578613457962, -0.008332331585609858] )
    s1_loc2 = np.array( [0.001522104293162247, 0.0027773313375925018, 0.00442505584256498, 0.007606205474409525, 0.01034704028479087, 0.014562872721971175, 0.017414496420364904, 0.02165021606546724, 0.026687636760153653, 0.03229383560501333, 0.03908291008944387, 0.04429741996194284, 0.05061021561626823, 0.0553640489152102, 0.06224041875115529, 0.0724474846764132, 0.07746182831676597, 0.08060437809901178, 0.08706735847054159] )
    s1_loc3 = np.array( [0.5516061024576036, 0.5753642848594115, 0.589362989371336, 0.6001896876074558, 0.6093421255842083, 0.6129361953658123, 0.6211566722588242, 0.6250181410806488, 0.6278757422484059, 0.6305787167353549, 0.6312466060294131, 0.6343298319024152, 0.6358119730645401, 0.6421623284642078, 0.6391172431614784, 0.6351499812276449, 0.637868735773629, 0.6393369041096401, 0.6388326152814826] )
    
    s1_spr1 = np.array( [-0.0018460464778439938, -0.0017628522648371918, -0.0016017941534079618, -0.0017953251687849669, -0.0017199782396935118, -0.0023705769114421146, -0.0023191860767870667, -0.0026871845573595904, -0.0033974373969778236, -0.0025853618953886968, -0.0028912562210840816, -0.003281222607193708, -0.003549540297251895, -0.004067358988499156, -0.004980100257737917, -0.003827128740740262, -0.004556290583375942, -0.005162953189749638, -0.005515035241890925] )
    s1_spr2 = np.array( [-0.033554165339405584, -0.03372191668925101, -0.03498335921892273, -0.03227454345448519, -0.031951350436769575, -0.026643952269486508, -0.027630178516384895, -0.025875262996821923, -0.02239585989169903, -0.026689023195920623, -0.025668458601714864, -0.02405958749301318, -0.023322606440787357, -0.02167188711157671, -0.01934415923816718, -0.02307842300716193, -0.021075461397864474, -0.019473551023907472, -0.01886459411294341] )
    
    s1_skw1 = np.array( [-0.5198621237985773, -0.17048270383433106, -0.03101419312189067, -0.00827221761735969, 0.007346354187485243, 0.009099838323959174, 0.013352372732172588, 0.01637653849317728, 0.02482698534998106, 0.0474871060260276, 0.061151158716832424, 0.06991473339433885, 0.08704593373143901, -0.0031297487419028602, 0.07497479925459888, 0.10203130694659046, 0.09365687309232823, 0.16399393764514797, 0.1997157367648677] )
    s1_skw2 = np.array( [-9.484558050287234, -7.842749123258372, -6.775447656214707, -6.669041835779461, -6.8344565364732945, -6.790501325088091, -6.848907297316231, -6.942285890849579, -7.045744900354655, -7.209722899096697, -7.354742540290536, -7.475437403186296, -7.643276873848059, -7.072451775300003, -7.769369069301989, -7.978203520676346, -8.079641941511527, -8.694513903231627, -8.968083892407783] )
    
    s1_scl1 = np.array( [0.04924324049329418, 0.0556939255257535, 0.06293338653864455, 0.06756659619897211, 0.0700310016708159, 0.07107448136694723, 0.07190234491069858, 0.07194632188360606, 0.07208070559320731, 0.07189871484064098, 0.07189907609208318, 0.07139239331173888, 0.07105556910661262, 0.0702623843821675, 0.0696987117431377, 0.06890499863105251, 0.06778313251482221, 0.06639758327222565, 0.06593154010105055] )
    s1_scl2 = np.array( [0.420809136256116, 0.43130743828096285, 0.41153198215604264, 0.45784692251907466, 0.4581157026509567, 0.5735119666664135, 0.594650905342458, 0.8797659102428912, 0.9542249205475535, 1.1129640815192627, 0.8604650839127875, 0.9953485446143463, 0.7988024030963862, 1.2378124599246663, 1.7894206352719224, 2.3309694466053674, 1.012530525658856, 2.0425955724088096, 3.001123492561699] )
    s1_scl3 = np.array( [31.292945552484476, 29.610937770821355, 28.218787017835734, 25.78452398378914, 24.541287542511768, 22.966048137090404, 21.950406329484807, 20.310078934674628, 19.149751021252353, 18.83974013226538, 17.68693659830355, 16.649774027364643, 16.221579042829674, 15.045768383994147, 14.508510376474202, 13.64070668765969, 13.48760146084981, 12.490037463709003, 11.976447731464903] )
    
    s2_loc1 = np.array( [-0.0006216070528639923, -0.0009370086485045864, -0.001513210520418146, -0.002288830315959099, -0.003001953755813691, -0.0038400210642196334, -0.004979935198489719, -0.005664700389136445, -0.007180504769766, -0.0082897159064698, -0.009504182415837146, -0.010740947226480727, -0.012122629296150328, -0.013781064510748772, -0.015191299863705342, -0.016921314205700977, -0.01811082074369924, -0.019035892650797196, -0.020554779576783425] )
    s2_loc2 = np.array( [0.009618217164921812, 0.01541939704354676, 0.02379908093938661, 0.033612000956514274, 0.04227366976213114, 0.05109141087518579, 0.06198826845745659, 0.06667838122401616, 0.08003561792696526, 0.08834002907666896, 0.09559950163845102, 0.10274705263985096, 0.11004678617258287, 0.11811514748933029, 0.12303911547686361, 0.12919132454799762, 0.13350796230047038, 0.13447288485635397, 0.13972930232712677] )
    s2_loc3 = np.array( [0.5704118200825119, 0.5984719950669539, 0.616593396471167, 0.6213893464945881, 0.625447574257471, 0.6285727689676972, 0.6276205275581046, 0.6398146725168448, 0.6295127742270255, 0.628102180893318, 0.630400200193272, 0.6300177067346429, 0.627092703069151, 0.6255890308979922, 0.6248273467589668, 0.623278954504306, 0.623406323374518, 0.6279374978791845, 0.625470988062128] )
    
    s2_spr1 = np.array( [-0.003142181869610132, -0.002779168918127837, -0.0029554283668137586, -0.0032957685725557052, -0.0030166093192402913, -0.004412769560026257, -0.00548287304749954, -0.002259957583495242, -0.004709146768999901, -0.0053889352293004875, -0.005909770619554512, -0.005949047417788438, -0.006156149019683593, -0.008422977703560111, -0.0071095392153472286, -0.006964784924264847, -0.006874112644686686, -0.008002537367724523, -0.008550984836670484] )
    s2_spr2 = np.array( [-0.024517022103479887, -0.03134209516588164, -0.02771015956252483, -0.02460234665568035, -0.026132332123926762, -0.020392508771788227, -0.016876191207547596, -0.03619475566313001, -0.022149870460476583, -0.02098515169686417, -0.01957117694174465, -0.01987739113359399, -0.02030327267060414, -0.014665658115529692, -0.018827559202755216, -0.01951212521927858, -0.01979320306023577, -0.017386549506144162, -0.017083915181414114] )
    
    s2_skw1 = np.array( [-0.12283400241727234, -0.03545669296303969, -0.002367882176534608, 0.019124682902109676, 0.06941860924477963, 0.07607468193839975, 0.07746936595051007, 0.1094935428533707, 0.11591692310498364, 0.19135362440793402, 0.1462674157562672, 0.12282115729257428, 0.29647566591173696, 0.16158749375802223, 0.33821039454303986, 0.3484940570824012, 0.2619365702017749, 0.1296238271494573, 0.27533212067987745] )
    s2_skw2 = np.array( [-7.270963491430534, -6.63616502162295, -6.66605269874495, -6.976925858444235, -7.409676389245323, -7.573629508785906, -7.809509063918554, -8.129255041260272, -8.417082491900512, -9.021113631317217, -8.960835058529035, -9.124267117314815, -10.186250273897375, -10.029989202256354, -10.96186409377742, -11.268032054517402, -11.256219927055358, -11.150137464824052, -11.957574893962] )
    
    s2_scl1 = np.array( [0.09359612425637162, 0.10454003635449885, 0.10720890085424714, 0.10770438887818481, 0.10714395323123706, 0.10616552333218415, 0.1048679780509145, 0.10250832763817785, 0.09998879096837375, 0.09724755242448788, 0.0952266031519336, 0.09258587380648334, 0.08935970785874155, 0.0868432819068363, 0.08407530457208608, 0.08136412259888537, 0.07939658078397141, 0.07786576142162233, 0.07629091689871849] )
    s2_scl2 = np.array( [0.6023455999750794, 0.539838550917827, 0.8078001559817628, 0.9428478243972757, 1.3545417017247368, 1.4306957217483052, 1.0130027861181772, 1.409906423937928, 2.0168894868004603, 2.516228330907928, 2.1375735500402824, 1.851478748661245, 3.3480956774784483, 1.7619077717472327, 2.923627432717212, 2.851276878358262, 4.30873695009166, 5.38346768994122, 4.627918318809291] )
    s2_scl3 = np.array( [23.715889686034476, 21.726665097570276, 19.743151823831738, 18.515221626175066, 17.251964300379136, 16.04161590076193, 15.037088714899516, 13.645856418906, 12.777637533958758, 12.04532255793417, 11.302981205486255, 10.844988310024313, 10.008987488244074, 9.814349343579089, 8.846341819203715, 8.413405693035092, 8.016568850622317, 7.54861187360059, 7.350948085044089] )
    
    s3_loc1 = np.array( [-0.0075932416148359085, -0.009247748944359806, -0.011860911560183736, -0.014378433448035735, -0.017903004479322717, -0.01993386049123194, -0.02267905092965833, -0.02521135264047676, -0.028165305947267516, -0.028969125389326063, -0.03318422856428786, -0.03580353701118423, -0.03561884052537826, -0.03334791349521078, -0.03568170488343325, -0.03647869598528013, -0.03652386316971154, -0.04389850694376288, -0.04019491525115987] )
    s3_loc2 = np.array( [0.08424234916310737, 0.09380254771592553, 0.11334297774737198, 0.12429166065797093, 0.13615388096090536, 0.14349421631859605, 0.14947624179444752, 0.1510272218625407, 0.15792295891889027, 0.15469779282231277, 0.162465268414832, 0.16470387130104475, 0.16377945232402585, 0.16182704610433202, 0.16342506591124517, 0.16128090110335513, 0.15616095556462678, 0.17337460598309962, 0.15858898944805755] )
    s3_loc3 = np.array( [0.6055429811862252, 0.6252159988849044, 0.6166451671813208, 0.6179869319561043, 0.6136378219409062, 0.6133415937439204, 0.6131535343961668, 0.6143133651275866, 0.6134059736658886, 0.6172070368516009, 0.6143520750825319, 0.6142339817069945, 0.612793124740459, 0.616288680303859, 0.6177292147564886, 0.6211139222503651, 0.6266748460392738, 0.6166618564153654, 0.6250609888718083] )
    
    s3_spr1 = np.array( [-0.006642392469790922, -0.006196122362821195, -0.006644692247341256, -0.007818116740397993, -0.008161446498438531, -0.008238449196233915, -0.008661936679081331, -0.009595620245680817, -0.01021461038074952, -0.0069604805250728565, -0.009099933957866731, -0.011933496347911476, -0.010798373666952271, -0.009837276968116046, -0.00925927389602342, -0.008986970153434366, -0.010409611168494471, -0.009328525716640498, -0.007999928563062954] )
    s3_spr2 = np.array( [-0.02263830122437223, -0.023610942373400785, -0.023096882935640384, -0.020734063536427386, -0.020829098253043736, -0.02066864122964892, -0.020301159791710162, -0.018838862909763762, -0.01822546314680574, -0.031038081530052053, -0.019999910033679916, -0.017084986893552583, -0.019040459973073846, -0.019996333002050816, -0.020620666820737096, -0.020296270950938874, -0.018544403170819176, -0.020591074106823187, -0.021565724403319584] )
    
    s3_skw1 = np.array( [0.13383680576035772, 0.12251994969713026, 0.18897816407101592, 0.10034624293651405, 0.0186944236544499, -0.10122085148122084, -0.25074786100942437, 0.19514765183784122, -0.316813558829006, 0.23459590964196222, -1.036552598125537, -0.4580133105152428, 1.198988343426421, 1.4338289349526376, 0.8623141380898063, 1.0942116492484355, 1.0508584743633462, 0.3493318172504608, 1.5215312259761191] )
    s3_skw2 = np.array( [-8.34867949837057, -8.781211151488694, -9.865515568120536, -10.413917659353686, -11.203827855581652, -11.559537835654531, -11.831092542711831, -13.346602844490016, -12.76493266612772, -14.045760324956095, -12.167762907306072, -13.526799069789874, -16.420248775179576, -17.15446546894872, -15.92547656628679, -16.123205297240872, -15.705050417763303, -15.362429192857167, -16.64834041179984] )
    
    s3_scl1 = np.array( [0.18424306759928982, 0.1759319140792425, 0.16710329743376845, 0.15786576280884773, 0.14999041060197793, 0.14210047920006036, 0.13546663859289876, 0.12952881711122113, 0.12447137231728232, 0.11939568456310423, 0.1148667086046596, 0.11159440983651243, 0.10630064447328944, 0.10278356761254234, 0.10043063879471531, 0.09979262250648963, 0.09613712979189191, 0.0941694111789057, 0.09131935723308825] )
    s3_scl2 = np.array( [1.201963165788038, 1.4636695082409203, 1.3222070771846324, 1.5760630652284573, 1.3101088210820524, 2.537771924757034, 2.0196666702769774, 3.78708846488212, 3.897723030103074, 3.945538855843666, 3.999234533903716, 4.152319565886069, 4.408612415416025, 4.658444127200636, 8.08474116538652, 3.41464539680847, 3.596965974818295, 3.334474229277263, 3.5511740783584784] )
    s3_scl3 = np.array( [13.034277825400125, 11.562452290115345, 11.109942980803687, 10.040201005506933, 8.907555425870122, 8.035640670984128, 7.54147043317759, 6.582781801431635, 6.342791911093519, 5.8980363132787765, 5.53146746421915, 5.255685007637995, 5.032228859314965, 5.212590185777826, 4.782116632141133, 4.8423712808547235, 4.672214803483415, 4.473747966872292, 4.293143968645818] )
    
    s4_loc1 = np.array( [-0.02094701885041686, -0.024106719994342246, -0.03157434953908525, -0.026439506310963992, -0.03927613387633342, -0.03758579639687871, -0.041787547249954496, -0.0485199026425437, -0.054446296290461965, -0.05075984558577511, -0.04689826374015514, -0.03751182738173382, -0.048929836787158704, -0.052783739800298574, -0.04616680767759821, -0.06622090757471455, -0.05481117326999676, -0.051598722152728455, -0.05652744441580001] )
    s4_loc2 = np.array( [0.14923088712525753, 0.14981617948506135, 0.17548531234486375, 0.14506731185582689, 0.17838954727248468, 0.16853818915230256, 0.17354131061686998, 0.17361892028112225, 0.17499318464941677, 0.16895274418112932, 0.17069783193487725, 0.14127988346961615, 0.16698346198913222, 0.17833128661847725, 0.15775468666107334, 0.18794017824817427, 0.1660294293811412, 0.15421600266858077, 0.15985275775264388] )
    s4_loc3 = np.array( [0.6022537202390641, 0.619187426483, 0.5960999927057604, 0.622627989737955, 0.6076284834639322, 0.6110707339692976, 0.6087930198803672, 0.6151475091911345, 0.609737307741119, 0.6075070607750118, 0.6160188898227628, 0.6271539029851652, 0.6169061399442537, 0.6042036926473557, 0.6155276117438518, 0.6116840987448917, 0.6176654194132466, 0.6225909812497675, 0.6218424742080951] )
    
    s4_spr1 = np.array( [-0.012736695050951454, -0.01242491079163017, -0.012867475470584366, -0.0068915525150267075, -0.012875339054715638, -0.011998611293403166, -0.011338692318643078, -0.012574076779864954, -0.012747629825931549, -0.010709530555682419, -0.03320376207443304, -0.019061086706111723, -0.03226874790828899, -0.0233649434393761, -0.006880606285362779, -0.007181728887535384, -0.008613859544273315, -0.010012520761098083, -0.012216638465688793] )
    s4_spr2 = np.array( [-0.017963395325946156, -0.0181583947193721, -0.016791645862834638, -0.036185614774877944, -0.018125042403306667, -0.01969880184312794, -0.020296095266950472, -0.017570650808186233, -0.01773418810886623, -0.018124535857509616, 0.009449255228155437, -0.006949674664326492, 0.005878835498509851, -0.005983339239436671, -0.023754375429041942, -0.02397293687411693, -0.020869155769369655, -0.01912551492316179, -0.017423669908040423] )
    
    s4_skw1 = np.array( [-0.5090713026640918, -0.7710847116249937, -0.9462894321490473, 1.35840129039326, -1.5135037132437181, 0.35449789232164364, 0.3002028073844769, -3.1616284645938957, -1.71272305064083, 0.8691413171796668, 1.519001499772762, 2.449602078429808, 1.497264609185763, 2.2634851250192085, 3.251516916515985, 0.5122161769618346, 2.26582156264224, 1.7189785445651498, 0.8229590663996739] )
    s4_skw2 = np.array( [-10.061523511147008, -10.498999955849452, -11.49339439559629, -16.159006734941574, -12.600949098380976, -15.040202727784692, -15.85242345952028, -11.44580192693116, -12.751013681618826, -14.378194139971285, -14.38826994967678, -15.046601997721472, -13.36973278739383, -14.376488979193322, -15.836167516136037, -13.105740980835934, -13.601128281203694, -11.685535626463734, -10.708689615179479] )
    
    s4_scl1 = np.array( [0.21261446588903649, 0.19778797152460276, 0.18602195554182654, 0.17543868598671897, 0.16783332176204294, 0.15842331592620157, 0.15339804431367599, 0.14653926176344534, 0.1422951455745492, 0.14003234608418652, 0.13362325123968247, 0.13809830964151307, 0.12448599453628748, 0.12074222688531075, 0.12075489311425042, 0.12403004148552337, 0.11805080137968413, 0.11540902729040461, 0.11498193710607349] )
    s4_scl2 = np.array( [2.113214410479939, 2.7540484376855447, 2.37432835608422, 2.9208714154613267, 2.0847310551420604, 4.291921777363918, 2.382924800780654, 4.177967159463819, 4.020323358888654, 2.0985565310836325, 5.426405591665324, 4.572668307281123, 6.02433303380532, 8.992666922911097, 2.692157646810233, 2.3884413998858403, 2.630923081709258, 2.574812590842238, 2.5690585485765136] )
    s4_scl3 = np.array( [8.452724236740258, 7.203301335737047, 6.54375257040071, 5.921728045923511, 5.593197854291994, 4.9735067942679745, 4.9017399737319725, 4.257763583039221, 3.66353747330715, 3.8287568707955817, 3.8486185677854605, 4.486952829276848, 3.495268185508556, 3.241432203940783, 3.404216203177379, 3.1768614206758032, 3.090430229944495, 2.9287132209795024, 2.779418098640927] )
    
    s5_loc1 = np.array( [-0.044279799801931516, -0.051672258134181345, -0.048568535536845155, -0.044740904520524254, -0.046014336844896586, -0.0601530728623453, -0.05005564342536106, -0.058878442410744095, -0.050199882453609075, -0.05271900570201736, -0.061692996520872075, -0.062462855961274426, -0.07999025488561948, -0.1170967566649451, -0.1157797303912001, -0.12986893362608476, -0.1499888140041534, -0.19030297327986376, -0.18252235812287312] )
    s5_loc2 = np.array( [0.2049805245663126, 0.2093093791256681, 0.183332483718736, 0.17161134532675643, 0.16863298144471672, 0.18963462736405373, 0.155122888327247, 0.16727924256590712, 0.15474647130914085, 0.15674153847784233, 0.166768915206302, 0.1689904658838058, 0.19698461345284615, 0.2515642279378572, 0.23660376714058765, 0.23301175914090988, 0.24164958270681003, 0.25359699069209063, 0.22403197294987953] )
    s5_loc3 = np.array( [0.5845105594588694, 0.5894565168869885, 0.607666975209493, 0.6117642230077092, 0.6117737832034117, 0.6039903862826604, 0.6208161246457662, 0.6155751352045539, 0.6228672593505462, 0.6202748443384056, 0.6176848457015246, 0.6156423105543801, 0.6031876634227332, 0.5910742772385771, 0.6002949396867958, 0.6024864935287769, 0.6068087908217379, 0.6114728261443632, 0.6175006343796574] )
    
    s5_spr1 = np.array( [-0.017845570087343846, -0.01851606723705877, -0.018439067453117994, -0.017073148019759316, -0.016375248258568016, -0.014556509274706517, -0.013610356941537637, -0.014909568707928077, -0.015328348779215973, -0.01656508672107019, -0.015414900144964872, -0.016615482473845707, -0.02642800689568358, -0.01724439470190845, -0.022686129191990295, -0.04270566168331014, -0.048311593228419505, -0.07516915641090433, -0.0851695499794885] )
    s5_spr2 = np.array( [-0.016988600164735138, -0.016998459159023375, -0.015970825619752046, -0.017555253757602102, -0.01784260317081343, -0.01926973995458993, -0.020153229501827023, -0.017794470640290803, -0.01623883961610349, -0.013621670496960947, -0.014713394836431862, -0.012982682599586846, -0.007065634052379128, -0.01446285180086991, -0.013317745112023011, -0.005530713118505689, -0.003514227248253927, 0.005648882497697905, 0.0075303027273217644] )
    
    s5_skw1 = np.array( [-1.6680009317915887, -2.0662181231082326, -2.285510552563751, -1.4458036098317588, -1.5063353390421315, -3.2318957639885673, -3.8508291006411497, -6.689671563435467, -1.423460978770257, -1.0660583223860507, -2.7689814608845866, -2.300857463952711, 2.110690471336119, 0.7148836056026738, 1.880375120420514, 4.941670681589093, 2.1985162351575713, 1.3679472637511747, 4.441245021877875] )
    s5_skw2 = np.array( [-11.156428880567923, -12.390942172312673, -11.407058587809644, -11.077825502190628, -9.010845568156835, -9.580043228300438, -7.59812353140007, -6.3242821283578525, -9.083741840215914, -7.908844041484327, -7.744090488718125, -6.623786459738085, -11.305769965936552, -9.85764636189263, -10.15136433664926, -12.003832243437401, -9.072851898024762, -8.44131493189448, -9.935718854295377] )
    
    s5_scl1 = np.array( [0.23044480900561967, 0.2167372030006432, 0.2040541484930587, 0.1948964938340224, 0.1868701297579938, 0.18077200036405183, 0.17216173901134776, 0.1689265461950643, 0.17112160233330068, 0.1609880145536174, 0.1605212850090278, 0.1530905026661633, 0.1530247043200589, 0.1563474524517103, 0.157226593166222, 0.15177881960672263, 0.15126430454968084, 0.1571396418037158, 0.1563561935532073] )
    s5_scl2 = np.array( [2.6651261371484223, 3.0376745664704092, 3.0952728305886774, 3.326955322458115, 2.9255373050504314, 3.6350775792800447, 5.29920543361931, 3.918189176112791, 2.4533494915475655, 2.882119412827967, 2.7260428703668307, 2.889753872732487, 2.581959920253705, 2.4063808427781637, 2.252164989005194, 2.414913967354397, 2.339740251252643, 2.3556764067914884, 2.4217151263722085] )
    s5_scl3 = np.array( [5.842877756252831, 5.047548819702113, 4.581409619119045, 4.326201343123971, 4.042961478771907, 3.6675259531613773, 3.307597056833786, 3.1651330639747957, 3.2420722601762053, 3.0531745600759734, 2.8479142633941255, 2.743758680339033, 2.5570261913775294, 2.2569760390011773, 2.1034295348101115, 1.9181727868117315, 1.8312251806457134, 1.6215125992170698, 1.4745718649433548] )   

## Spline Fitting
    iz = np.size(sol_d)
    jz = np.size(tsr_d)
    
    # Initializing rectangular matrices
    Z_loc1 = np.zeros((iz,jz))
    Z_loc2 = np.zeros((iz,jz))
    Z_loc3 = np.zeros((iz,jz))
    Z_spr1 = np.zeros((iz,jz))
    Z_spr2 = np.zeros((iz,jz))
    Z_skw1 = np.zeros((iz,jz))
    Z_skw2 = np.zeros((iz,jz))
    Z_scl1 = np.zeros((iz,jz))
    Z_scl2 = np.zeros((iz,jz))
    Z_scl3 = np.zeros((iz,jz))
    
    # Transferring raw data into rectangular matrices
    for i in range(iz):
        for j in range(jz):
            sol = str(i+1)
            exec('Z_loc1[i,j] = s'+sol+'_loc1[j]')
            exec('Z_loc2[i,j] = s'+sol+'_loc2[j]')
            exec('Z_loc3[i,j] = s'+sol+'_loc3[j]')
            exec('Z_spr1[i,j] = s'+sol+'_spr1[j]')
            exec('Z_spr2[i,j] = s'+sol+'_spr2[j]')
            exec('Z_skw1[i,j] = s'+sol+'_skw1[j]')
            exec('Z_skw2[i,j] = s'+sol+'_skw2[j]')
            exec('Z_scl1[i,j] = s'+sol+'_scl1[j]')
            exec('Z_scl2[i,j] = s'+sol+'_scl2[j]')
            exec('Z_scl3[i,j] = s'+sol+'_scl3[j]')
    
    # Creating a rectangular bivariate spline of the parameter data
    s_loc1 = RectBivariateSpline(sol_d,tsr_d,Z_loc1)
    s_loc2 = RectBivariateSpline(sol_d,tsr_d,Z_loc2)
    s_loc3 = RectBivariateSpline(sol_d,tsr_d,Z_loc3)
    s_spr1 = RectBivariateSpline(sol_d,tsr_d,Z_spr1)
    s_spr2 = RectBivariateSpline(sol_d,tsr_d,Z_spr2)
    s_skw1 = RectBivariateSpline(sol_d,tsr_d,Z_skw1)
    s_skw2 = RectBivariateSpline(sol_d,tsr_d,Z_skw2)
    s_scl1 = RectBivariateSpline(sol_d,tsr_d,Z_scl1)
    s_scl2 = RectBivariateSpline(sol_d,tsr_d,Z_scl2)
    s_scl3 = RectBivariateSpline(sol_d,tsr_d,Z_scl3)
    
    # Selecting the specific parameters to use for TSR and solidity
    loc1 = s_loc1(solidity,tsr)
    loc2 = s_loc2(solidity,tsr)
    loc3 = s_loc3(solidity,tsr)
    spr1 = s_spr1(solidity,tsr)
    spr2 = s_spr2(solidity,tsr)
    skw1 = s_skw1(solidity,tsr)
    skw2 = s_skw2(solidity,tsr)
    scl1 = s_scl1(solidity,tsr)
    scl2 = s_scl2(solidity,tsr)
    scl3 = s_scl3(solidity,tsr)
    
    # Creating arrays of the parameters
    loc = np.array([loc1[0,0],loc2[0,0],loc3[0,0]])
    spr = np.array([spr1[0,0],spr2[0,0]])
    skw = np.array([skw1[0,0],skw2[0,0]])
    scl = np.array([scl1[0,0],scl2[0,0],scl3[0,0]])
    
    return loc,spr,skw,scl

## Final Velocity Field (using both methods)
def velocity_field(x0,y0,velf,dia,tsr,solidity):
    """
    Calculating normalized velocity from the vorticity data at (x0,y0)
    
    Parameters
    ----------
    x0 : float
        downstream distance in flow domain (m)
    y0 : float
        lateral distance in flow domation (m)
    velf : float
        free stream velocity (m/s)
    dia : float
        turbine diameter (m)
    tsr : float
        tip-speed ratio
    solidity : float
        turbine solidity
    
    Returns
    ----------
    vel : float
        final normalized velocity at (x0,y0) with respect to the free stream velocity (m/s)
    """
    rad = dia/2.
    rot = tsr*velf/rad

    # Calculating EMG distribution parameters
    loc,spr,skw,scl = vorticity(tsr,solidity)
    
    # Integration of the vorticity profile using Fortran code (vorticity.f90; _vortrun.so)
    vel_vs = dblquad(_vortrun.integrand,0.,35.*dia,lambda x: -4.*dia,lambda x: 4.*dia, args=(x0,y0,dia,loc[0],loc[1],loc[2],spr[0],spr[1],skw[0],skw[1],scl[0],scl[1],scl[2]))
    
    # Calculating velocity deficit
    vel = (vel_vs[0]*(rot))/(2.*pi)
    vel = (vel + velf)/velf # normalization of velocity
    
    return vel
