var Module=typeof pyodide._module!=="undefined"?pyodide._module:{};Module.checkABI(1);if(!Module.expectedDataFileDownloads){Module.expectedDataFileDownloads=0;Module.finishedDataFileDownloads=0}Module.expectedDataFileDownloads++;(function(){var loadPackage=function(metadata){var PACKAGE_PATH;if(typeof window==="object"){PACKAGE_PATH=window["encodeURIComponent"](window.location.pathname.toString().substring(0,window.location.pathname.toString().lastIndexOf("/"))+"/")}else if(typeof location!=="undefined"){PACKAGE_PATH=encodeURIComponent(location.pathname.toString().substring(0,location.pathname.toString().lastIndexOf("/"))+"/")}else{throw"using preloaded data can only be done on a web page or in a web worker"}var PACKAGE_NAME="cytoolz.data";var REMOTE_PACKAGE_BASE="cytoolz.data";if(typeof Module["locateFilePackage"]==="function"&&!Module["locateFile"]){Module["locateFile"]=Module["locateFilePackage"];err("warning: you defined Module.locateFilePackage, that has been renamed to Module.locateFile (using your locateFilePackage for now)")}var REMOTE_PACKAGE_NAME=Module["locateFile"]?Module["locateFile"](REMOTE_PACKAGE_BASE,""):REMOTE_PACKAGE_BASE;var REMOTE_PACKAGE_SIZE=metadata.remote_package_size;var PACKAGE_UUID=metadata.package_uuid;function fetchRemotePackage(packageName,packageSize,callback,errback){var xhr=new XMLHttpRequest;xhr.open("GET",packageName,true);xhr.responseType="arraybuffer";xhr.onprogress=function(event){var url=packageName;var size=packageSize;if(event.total)size=event.total;if(event.loaded){if(!xhr.addedTotal){xhr.addedTotal=true;if(!Module.dataFileDownloads)Module.dataFileDownloads={};Module.dataFileDownloads[url]={loaded:event.loaded,total:size}}else{Module.dataFileDownloads[url].loaded=event.loaded}var total=0;var loaded=0;var num=0;for(var download in Module.dataFileDownloads){var data=Module.dataFileDownloads[download];total+=data.total;loaded+=data.loaded;num++}total=Math.ceil(total*Module.expectedDataFileDownloads/num);if(Module["setStatus"])Module["setStatus"]("Downloading data... ("+loaded+"/"+total+")")}else if(!Module.dataFileDownloads){if(Module["setStatus"])Module["setStatus"]("Downloading data...")}};xhr.onerror=function(event){throw new Error("NetworkError for: "+packageName)};xhr.onload=function(event){if(xhr.status==200||xhr.status==304||xhr.status==206||xhr.status==0&&xhr.response){var packageData=xhr.response;callback(packageData)}else{throw new Error(xhr.statusText+" : "+xhr.responseURL)}};xhr.send(null)}function handleError(error){console.error("package error:",error)}var fetchedCallback=null;var fetched=Module["getPreloadedPackage"]?Module["getPreloadedPackage"](REMOTE_PACKAGE_NAME,REMOTE_PACKAGE_SIZE):null;if(!fetched)fetchRemotePackage(REMOTE_PACKAGE_NAME,REMOTE_PACKAGE_SIZE,function(data){if(fetchedCallback){fetchedCallback(data);fetchedCallback=null}else{fetched=data}},handleError);function runWithFS(){function assert(check,msg){if(!check)throw msg+(new Error).stack}Module["FS_createPath"]("/","lib",true,true);Module["FS_createPath"]("/lib","python3.7",true,true);Module["FS_createPath"]("/lib/python3.7","site-packages",true,true);Module["FS_createPath"]("/lib/python3.7/site-packages","cytoolz-0.10.0-py3.7.egg-info",true,true);Module["FS_createPath"]("/lib/python3.7/site-packages","cytoolz",true,true);Module["FS_createPath"]("/lib/python3.7/site-packages/cytoolz","tests",true,true);Module["FS_createPath"]("/lib/python3.7/site-packages/cytoolz","curried",true,true);function DataRequest(start,end,audio){this.start=start;this.end=end;this.audio=audio}DataRequest.prototype={requests:{},open:function(mode,name){this.name=name;this.requests[name]=this;Module["addRunDependency"]("fp "+this.name)},send:function(){},onload:function(){var byteArray=this.byteArray.subarray(this.start,this.end);this.finish(byteArray)},finish:function(byteArray){var that=this;Module["FS_createPreloadedFile"](this.name,null,byteArray,true,true,function(){Module["removeRunDependency"]("fp "+that.name)},function(){if(that.audio){Module["removeRunDependency"]("fp "+that.name)}else{err("Preloading file "+that.name+" failed")}},false,true);this.requests[this.name]=null}};function processPackageData(arrayBuffer){Module.finishedDataFileDownloads++;assert(arrayBuffer,"Loading data file failed.");assert(arrayBuffer instanceof ArrayBuffer,"bad input to processPackageData");var byteArray=new Uint8Array(arrayBuffer);var curr;var compressedData={data:null,cachedOffset:650298,cachedIndexes:[-1,-1],cachedChunks:[null,null],offsets:[0,1050,2405,3512,4879,6041,7357,8332,8965,9713,10276,11075,11764,12417,13087,13568,14522,15810,16471,17389,18316,19173,19883,20832,21382,21941,22485,22943,23448,23801,24481,25185,25825,26321,26867,27380,27870,28565,29285,30048,30904,31776,32745,32999,33262,34058,34577,35100,35509,36057,37080,37746,38654,39663,40278,41166,41929,42705,43365,44021,44571,45172,46063,46922,47641,48245,49006,49643,49952,50543,51256,51949,52681,53238,53644,54039,54267,54928,55615,56146,57079,57478,58174,58649,59399,60311,60908,61937,62612,63366,64138,64902,65578,66218,66864,67671,68351,69161,69935,70632,71754,72398,73171,73830,74534,75518,76011,76572,77433,78182,78582,79030,79789,80466,81225,81710,82817,83574,84359,84943,85251,85862,86504,87070,87831,88460,89016,89807,90488,91285,92016,92695,93572,94276,94874,95826,96402,97044,97742,98341,98928,99723,100597,101177,101863,102916,103611,104317,105199,105868,106555,107606,108036,108841,109696,110478,111047,111564,112410,113038,113585,114306,115055,115758,116420,116823,117154,117386,118163,118925,120203,120880,121574,122166,122899,123522,124470,125392,126255,127507,128251,128777,129891,131205,132476,133460,134443,135437,136435,137507,138686,139842,140354,140954,141541,142018,143259,144416,145621,146761,147620,148977,150071,151081,151231,152289,153752,154960,155911,156954,158109,158877,159596,160844,162135,162980,163884,164650,165641,166492,167332,168223,168909,169593,170334,170879,171393,171886,172442,173254,174159,175151,175386,175566,176397,176976,177700,178310,178923,179863,180422,181325,182001,182647,183338,184099,184681,185436,185860,186506,187232,187845,188588,189260,189933,190581,191368,192183,192904,193618,194397,195092,195812,196560,197213,198014,198799,199481,200268,200933,201670,202445,202907,203308,204318,205324,206064,206891,207789,208754,209407,210231,210808,211335,212185,213018,213869,214702,215721,216734,217993,219375,220836,221831,222876,223388,223988,224843,226027,227272,228461,229329,230497,231503,232756,233277,234445,235261,236062,237367,238590,239768,240548,241658,242781,243836,244825,245955,247176,248462,249605,250747,252016,252857,254051,255236,256031,256829,257682,258526,259412,260487,261626,262807,264188,265396,266430,267471,268333,269312,270029,270689,271382,271826,272289,272958,273582,274287,275148,276125,276380,276547,277364,277942,279027,279485,280184,280814,281626,282290,283152,284363,285759,286999,287422,288196,289502,290825,291947,293198,294313,295141,296138,297008,297722,298268,298805,299342,300220,301106,301479,301757,302487,303029,303813,305157,306015,306501,307437,308208,308915,309576,310991,311391,312511,313895,315178,316580,317738,318776,319552,320735,322017,323192,324327,325658,326888,328052,329340,330327,331028,331559,332093,332628,333259,333858,334476,335093,335779,336496,337059,337567,338066,338590,339224,339809,340394,340969,341732,342582,343699,344291,344902,345599,346296,347028,347636,348286,348941,349581,350179,350847,351569,352085,352674,353161,353803,354337,354862,355361,355842,356336,356798,357254,357767,358231,358744,359218,359756,360251,360730,361238,361714,362369,363138,363614,364082,364552,365030,365493,365974,366451,366918,367631,368342,368978,369479,370282,370991,372706,373779,374846,375778,376714,377588,378440,379124,380021,380609,381200,381796,382703,383595,384598,384812,385022,385855,386437,387155,387881,388604,389239,390017,390453,391270,392166,392732,393554,394145,394796,395273,396095,396675,397366,398092,398850,399611,400252,401182,401888,402712,403494,404058,404710,405493,406124,406999,407858,408640,409358,410096,411047,411783,412497,413396,414197,414892,415571,416509,417211,417969,418760,419560,420243,421017,421845,422538,423270,424027,424719,425602,426180,426962,427604,428299,429015,429606,430217,430924,431587,432293,432838,433765,434979,435852,436513,437328,437878,438382,439047,439830,440388,440957,441695,442383,443110,443675,444257,444902,445584,446280,447e3,447713,448289,448889,449807,450802,451369,451966,452583,453199,454138,454878,455758,456469,456895,457366,458290,458613,458949,459578,460392,460968,461692,462146,463024,463690,464345,464951,465908,466490,466980,467543,468139,469095,469748,470335,471163,471934,472841,473416,473945,474842,475480,476246,477255,477910,478450,479076,479908,480870,481594,482457,483069,484051,484716,485577,486385,486979,488005,488784,489639,490594,491445,492380,493300,493950,494467,494679,494900,495700,496707,497277,498047,498634,499454,500176,501052,501449,502241,502798,503438,504175,505019,505538,506328,506907,507361,507738,508112,508503,509093,509768,510666,511562,512271,512864,513603,514668,515393,516086,516824,517576,518560,519202,520119,521165,522221,523081,524014,525337,526073,527284,528549,529965,530924,531692,532713,533813,534412,535234,536423,537613,538774,539959,541372,542372,543364,544347,545348,546336,547334,548328,549520,550683,551841,552984,554114,555282,556357,556821,557494,558130,558709,559170,559716,561138,562382,563765,565001,566121,567075,567828,568801,569199,569565,569969,571225,572272,573665,574860,576154,577516,577947,578115,578225,578275,578357,579809,580689,581828,582682,583749,584332,584779,585417,586608,587778,588922,589766,591104,592043,593161,594148,595456,596602,597599,598735,599948,601226,602284,603378,604423,605342,605960,607072,607975,608829,609768,610765,611767,612782,613551,614476,615491,616442,617577,618519,619574,620301,621357,622346,623490,624562,625807,626961,628035,628748,629892,631092,632258,633555,634547,635275,636062,636714,637300,638167,638955,639692,640832,641814,642828,643331,643817,644626,645351,646068,647094,648197,649394],sizes:[1050,1355,1107,1367,1162,1316,975,633,748,563,799,689,653,670,481,954,1288,661,918,927,857,710,949,550,559,544,458,505,353,680,704,640,496,546,513,490,695,720,763,856,872,969,254,263,796,519,523,409,548,1023,666,908,1009,615,888,763,776,660,656,550,601,891,859,719,604,761,637,309,591,713,693,732,557,406,395,228,661,687,531,933,399,696,475,750,912,597,1029,675,754,772,764,676,640,646,807,680,810,774,697,1122,644,773,659,704,984,493,561,861,749,400,448,759,677,759,485,1107,757,785,584,308,611,642,566,761,629,556,791,681,797,731,679,877,704,598,952,576,642,698,599,587,795,874,580,686,1053,695,706,882,669,687,1051,430,805,855,782,569,517,846,628,547,721,749,703,662,403,331,232,777,762,1278,677,694,592,733,623,948,922,863,1252,744,526,1114,1314,1271,984,983,994,998,1072,1179,1156,512,600,587,477,1241,1157,1205,1140,859,1357,1094,1010,150,1058,1463,1208,951,1043,1155,768,719,1248,1291,845,904,766,991,851,840,891,686,684,741,545,514,493,556,812,905,992,235,180,831,579,724,610,613,940,559,903,676,646,691,761,582,755,424,646,726,613,743,672,673,648,787,815,721,714,779,695,720,748,653,801,785,682,787,665,737,775,462,401,1010,1006,740,827,898,965,653,824,577,527,850,833,851,833,1019,1013,1259,1382,1461,995,1045,512,600,855,1184,1245,1189,868,1168,1006,1253,521,1168,816,801,1305,1223,1178,780,1110,1123,1055,989,1130,1221,1286,1143,1142,1269,841,1194,1185,795,798,853,844,886,1075,1139,1181,1381,1208,1034,1041,862,979,717,660,693,444,463,669,624,705,861,977,255,167,817,578,1085,458,699,630,812,664,862,1211,1396,1240,423,774,1306,1323,1122,1251,1115,828,997,870,714,546,537,537,878,886,373,278,730,542,784,1344,858,486,936,771,707,661,1415,400,1120,1384,1283,1402,1158,1038,776,1183,1282,1175,1135,1331,1230,1164,1288,987,701,531,534,535,631,599,618,617,686,717,563,508,499,524,634,585,585,575,763,850,1117,592,611,697,697,732,608,650,655,640,598,668,722,516,589,487,642,534,525,499,481,494,462,456,513,464,513,474,538,495,479,508,476,655,769,476,468,470,478,463,481,477,467,713,711,636,501,803,709,1715,1073,1067,932,936,874,852,684,897,588,591,596,907,892,1003,214,210,833,582,718,726,723,635,778,436,817,896,566,822,591,651,477,822,580,691,726,758,761,641,930,706,824,782,564,652,783,631,875,859,782,718,738,951,736,714,899,801,695,679,938,702,758,791,800,683,774,828,693,732,757,692,883,578,782,642,695,716,591,611,707,663,706,545,927,1214,873,661,815,550,504,665,783,558,569,738,688,727,565,582,645,682,696,720,713,576,600,918,995,567,597,617,616,939,740,880,711,426,471,924,323,336,629,814,576,724,454,878,666,655,606,957,582,490,563,596,956,653,587,828,771,907,575,529,897,638,766,1009,655,540,626,832,962,724,863,612,982,665,861,808,594,1026,779,855,955,851,935,920,650,517,212,221,800,1007,570,770,587,820,722,876,397,792,557,640,737,844,519,790,579,454,377,374,391,590,675,898,896,709,593,739,1065,725,693,738,752,984,642,917,1046,1056,860,933,1323,736,1211,1265,1416,959,768,1021,1100,599,822,1189,1190,1161,1185,1413,1e3,992,983,1001,988,998,994,1192,1163,1158,1143,1130,1168,1075,464,673,636,579,461,546,1422,1244,1383,1236,1120,954,753,973,398,366,404,1256,1047,1393,1195,1294,1362,431,168,110,50,82,1452,880,1139,854,1067,583,447,638,1191,1170,1144,844,1338,939,1118,987,1308,1146,997,1136,1213,1278,1058,1094,1045,919,618,1112,903,854,939,997,1002,1015,769,925,1015,951,1135,942,1055,727,1056,989,1144,1072,1245,1154,1074,713,1144,1200,1166,1297,992,728,787,652,586,867,788,737,1140,982,1014,503,486,809,725,717,1026,1103,1197,904],successes:[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]};compressedData.data=byteArray;assert(typeof Module.LZ4==="object","LZ4 not present - was your app build with  -s LZ4=1  ?");Module.LZ4.loadPackage({metadata:metadata,compressedData:compressedData});Module["removeRunDependency"]("datafile_cytoolz.data")}Module["addRunDependency"]("datafile_cytoolz.data");if(!Module.preloadResults)Module.preloadResults={};Module.preloadResults[PACKAGE_NAME]={fromCache:false};if(fetched){processPackageData(fetched);fetched=null}else{fetchedCallback=processPackageData}}if(Module["calledRun"]){runWithFS()}else{if(!Module["preRun"])Module["preRun"]=[];Module["preRun"].push(runWithFS)}};loadPackage({files:[{filename:"/lib/python3.7/site-packages/cytoolz-0.10.0-py3.7.egg-info/SOURCES.txt",start:0,end:1365,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz-0.10.0-py3.7.egg-info/not-zip-safe",start:1365,end:1366,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz-0.10.0-py3.7.egg-info/top_level.txt",start:1366,end:1374,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz-0.10.0-py3.7.egg-info/dependency_links.txt",start:1374,end:1375,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz-0.10.0-py3.7.egg-info/requires.txt",start:1375,end:1388,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz-0.10.0-py3.7.egg-info/PKG-INFO",start:1388,end:6284,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/utils.pxd",start:6284,end:6317,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/recipes.pxd",start:6317,end:6417,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/functoolz.so",start:6417,end:429485,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/itertoolz.pxd",start:429485,end:434180,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/dicttoolz.so",start:434180,end:626398,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/__init__.py",start:626398,end:626883,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/_signatures.py",start:626883,end:631239,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/itertoolz.pyx",start:631239,end:682452,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/__init__.pxd",start:682452,end:683202,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/recipes.so",start:683202,end:752104,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/functoolz.pxd",start:752104,end:753356,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/utils.so",start:753356,end:808443,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/recipes.pyx",start:808443,end:810081,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/cpython.pxd",start:810081,end:810578,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/dicttoolz.pyx",start:810578,end:826085,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/_version.py",start:826085,end:826137,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/compatibility.py",start:826137,end:827211,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/utils_test.py",start:827211,end:829286,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/itertoolz.so",start:829286,end:1548136,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/utils.pyx",start:1548136,end:1549489,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/dicttoolz.pxd",start:1549489,end:1550857,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/functoolz.pyx",start:1550857,end:1576023,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_curried.py",start:1576023,end:1579726,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_compatibility.py",start:1579726,end:1580273,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_serialization.py",start:1580273,end:1586167,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_itertoolz.py",start:1586167,end:1604380,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_functoolz.py",start:1604380,end:1624731,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_docstrings.py",start:1624731,end:1627765,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_tlz.py",start:1627765,end:1629251,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/dev_skip_test.py",start:1629251,end:1630254,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_signatures.py",start:1630254,end:1633187,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_embedded_sigs.py",start:1633187,end:1636682,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_recipes.py",start:1636682,end:1637504,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_curried_toolzlike.py",start:1637504,end:1638903,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_dev_skip_test.py",start:1638903,end:1639283,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_utils.py",start:1639283,end:1639668,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_none_safe.py",start:1639668,end:1651890,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_doctests.py",start:1651890,end:1652325,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_dicttoolz.py",start:1652325,end:1661270,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/tests/test_inspect_args.py",start:1661270,end:1677522,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/curried/__init__.py",start:1677522,end:1680406,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/curried/exceptions.py",start:1680406,end:1680756,audio:0},{filename:"/lib/python3.7/site-packages/cytoolz/curried/operator.py",start:1680756,end:1681258,audio:0}],remote_package_size:654394,package_uuid:"ba448248-63bb-4783-87aa-aca8714ab02a"})})();