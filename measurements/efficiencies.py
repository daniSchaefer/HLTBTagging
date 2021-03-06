import os, time
import json
import logging
import logging.config
from modules.utils import setup_logging, getLabel

def efficiencies(loglev, run, doMC, doData, doCSV, doDeepCSV, CSVWPs, DeepCSVWPs, ptordered, csvordered, doinclusive, nInclusiveIter, dosplit, nSplitIter, doCross, compWPs, looseSel):
    import ROOT

    import modules.classes
    import modules.effPlots
    
    setup_logging(loglevel = loglev, logname = "efficiencyoutput", errname = "efficiencyerror")

    logger = logging.getLogger(__name__)

    logger.info("Starting shape comparison")
    t0 = time.time()
    
    if not (doMC or doData):
        if __name__ == "__main__":
            logging.warning("At least on of the flags --mc and --data should to be set")
            logging.warning("Falling back the only mc")
        else:
            logging.warning("At least on of the paramters doMC and doData should to be set")
            logging.warning("Falling back the only mc")
        doMC = True

    if not (ptordered or csvordered):
        if __name__ == "__main__":
            logging.warning("At least on of the flags --ptorderd and --csvordered should to be set")
            logging.warning("Falling back to pt ordered")
        else:
            logging.warning("At least on of the paramters ptordered and ptordered should to be set")
            logging.warning("Falling back to pt ordered")
        ptordered = True
    
    if loglev > 0:
        ROOT.gErrorIgnoreLevel = ROOT.kBreak# kPrint, kInfo, kWarning, kError, kBreak, kSysError, kFatal;

    if run == "CD":
        DataInput = "/mnt/t3nfs01/data01/shome/koschwei/scratch/HLTBTagging/DiLepton_v8/MuonEG/MuonEG_RunCD_phase1_0p9970p996_mod_mod_mod.root"
        basepaths = "v8nTuples/Efficiencies/RunCD/"
        fileprefix = "RunCD_"
    if run == "E":
        DataInput = "/mnt/t3nfs01/data01/shome/koschwei/scratch/HLTBTagging/DiLepton_v8/MuonEG/RunE/phase1/MuonEG_RunE_phase1_mod_mod_mod.root"
        basepaths = "v8nTuples/Efficiencies/RunE/"
        fileprefix = "RunE_EmilSel_"
    if run == "F":
        DataInput = "/mnt/t3nfs01/data01/shome/koschwei/scratch/HLTBTagging/DiLepton_v8/MuonEG/RunF/phase1/MuonEG_RunF_phase1_mod_mod_mod.root"
        basepaths = "v8nTuples/Efficiencies/RunF/"
        fileprefix = "RunF_"

    if run == "Test":
        DataInput = "/mnt/t3nfs01/data01/shome/koschwei/trigger/onlineBTV/CMSSW_9_2_12_patch1/src/HLTBTagging/nTuples/tree_phase1.root"
        basepaths = "testing/emilComp3K/"
        fileprefix = "Tesing_"
        

    #MCInput = "/mnt/t3nfs01/data01/shome/koschwei/scratch/HLTBTagging/DiLepton_v3/ttbar/ttbar_v3.root"
    MCInput = "/mnt/t3nfs01/data01/shome/koschwei/scratch/HLTBTagging/DiLepton_v8/ttbar/phase1/ttbar_0p85_mod_mod_mod.root"
    
    MCSelection = "1"
    VarSelection = "1"



    DeepCSVSelWP = "0.8958"
    if looseSel:
        TriggerSelection = "1"
        LeptonSelection = "1"
        offlineSelection = "1"
        CSVSelection = "1"

    else:
        TriggerSelection = "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v4 > 0 || HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v4 > 0"
        LeptonSelection = "Sum$((abs(offTightElectrons_superClusterEta) <= 1.4442 || abs(offTightElectrons_superClusterEta) >= 1.5660) && offTightElectrons_pt > 30 && abs(offTightElectrons_eta) < 2.4) > 0 && Sum$(offTightMuons_iso < 0.25 && offTightMuons_pt > 20 && abs(offTightMuons_eta) < 2.4) > 0"
        offlineSelection = "Sum$(cleanJets_pt > 30 && abs(cleanJets_eta) < 2.4) > 2"
        CSVSelection = "Sum$(cleanJets_deepcsv > {0}) >= 1".format(DeepCSVSelWP)



    logging.info("Using: doMC: {0} | doData: {1} | doCSV: {2} | doDeepCSV: {3}".format(doMC, doData, doCSV, doDeepCSV))




    samples = []
    if doMC:
        eventSelection = "({0}) && ({1}) && ({2}) && ({3})".format(VarSelection, TriggerSelection, LeptonSelection, MCSelection)
        samples.append( (modules.classes.Sample("ttbar", MCInput, eventSelection, 831.76, 4591.622871124, ROOT.kRed, 9937324, legendText = "Dataset: t#bar{t}"), "MC", getLabel("Dataset: t#bar{t}", 0.7)) )
    if doData:
        eventSelection = "({0}) && ({1}) && ({2})".format(VarSelection, TriggerSelection, LeptonSelection)
        samples.append( (modules.classes.Sample("data", DataInput, eventSelection, legendText = "Dataset: MuonEG"),"MuonEG", getLabel("Dataset: MuonEG", 0.7)) )

    CSVSelWP = "0.9535"

    

    WPColors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kPink+7, ROOT.kViolet, ROOT.kCyan]
    
    #CSVSelection = "Sum$(cleanJets_csv > {0}) >= 1".format(CSVSelWP)


    refbyCSVRank = { 0 : "cleanJets_ileadingCSV",
                     1 : "cleanJets_isecondCSV",
                     2 : "cleanJets_ithirdCSV",
                     3 : "cleanJets_ifourthCSV"}

    refbyDeepCSVRank = { 0 : "cleanJets_ileadingDeepCSV",
                         1 : "cleanJets_isecondDeepCSV",
                         2 : "cleanJets_ithirdDeepCSV",
                         3 : "cleanJets_ifourthDeepCSV"}


    
    if doCSV:
        logging.info("Processing plots for CSV")
        CSVPlotBaseObjs = {}


        collections = []
        if ptordered:
            #collections.append( ("pT", "cleanJets") )
            collections.append( ("pT", "offJets") )
            logging.debug("Adding {1} to collecton as ordered by {0}".format("ptOrdered", "offJets"))
        if csvordered:                
            collections.append( ("CSV", "cleanCSVJets") )
            logging.debug("Adding {1} to collecton as ordered by {0}".format("csvOrdered", "cleanCSVJets"))
        
        for WP in CSVWPs:
            WPLabel = getLabel("PF WP: {0}".format(WP), 0.7, "under")
            CaloWPLabel = getLabel("Calo WP: {0}".format(WP), 0.7, "under")
            logging.info("Using WP: {0}".format(WP))
            for collectionName, collection in collections:

                if dosplit:
                    for i in range(nSplitIter):
                        if looseSel:
                            JetSelection = "abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30".format(i, collection)
                        else:
                            JetSelection = "abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30 && {1}_passesTightLeptVetoID[{0}] > 0".format(i, collection)

                        logging.info("Making effciency for Jet {0} ordered by {1} w/ CSV as tagger".format(i, collectionName))
                        logging.subinfo("Using collection: {0}".format(collection))
                        CSVPlotBaseObjs[i] = modules.classes.PlotBase("{1}_csv[{0}]".format(i, collection),
                                                                      "{0} && {1} && ({2})".format(CSVSelection, offlineSelection, JetSelection),
                                                                      "1",
                                                                      [20,0,1],
                                                                      modules.utils.getAxisTitle("csv", i, collectionName.lower()),
                                                                      LegendPosition = [0.1,0.6,0.4,0.76])

                        CSVPlotBaseObjs[i].color = WPColors[i]
                        onlysamples = []

                        for sampleStuff in samples:
                            sample, name, label = sampleStuff
                            onlysamples.append(sample)
                            if not (doMC and doData):
                                modules.effPlots.makeEffPlot(CSVPlotBaseObjs[i], sample,
                                                             "pfJets_csv[{2}_matchPF[{1}]] >= {0}".format(WP, i, collection),
                                                             basepaths+"CSV/{3}/{4}Eff_{2}_Jet{0}_pfWP_{1}_CSV_order{3}".format(i, WP, name, collectionName, fileprefix),
                                                             addSel = "{1}_matchPF[{0}] >= 0".format(i, collection),
                                                             label = [label,WPLabel])

                                modules.effPlots.makeEffPlot(CSVPlotBaseObjs[i], sample,
                                                             "caloJets_csv[{2}_matchCalo[{1}]] >= {0}".format(WP, i, collection),
                                                             basepaths+"CSV/{3}/{4}Eff_{2}_Jet{0}_caloWP_{1}_CSV_order{3}".format(i, WP, name, collectionName, fileprefix),
                                                             addSel = "{1}_matchCalo[{0}] >= 0".format(i, collection),
                                                             label = [label,CaloWPLabel])

                        if doMC and doData:
                            modules.effPlots.makeEffSCompPlot(CSVPlotBaseObjs[i], onlysamples,
                                                              "pfJets_csv[{2}_matchPF[{1}]] >= {0}".format(WP, i, collection),
                                                              basepaths+"CSV/{2}/{3}Eff_DataMC_Jet{0}_pfWP_{1}_CSV_order{2}".format(i, WP, collectionName, fileprefix),
                                                              addSel = "{1}_matchPF[{0}] >= 0".format(i, collection),
                                                              label = WPLabel)
                            modules.effPlots.makeEffSCompPlot(CSVPlotBaseObjs[i], onlysamples,
                                                              "caloJets_csv[{2}_matchCalo[{1}]] >= {0}".format(WP, i, collection),
                                                              basepaths+"CSV/{2}/{3}Eff_DataMC_Jet{0}_caloWP_{1}_CSV_order{2}".format(i, WP, collectionName, fileprefix),
                                                              addSel = "{1}_matchCalo[{0}] >= 0".format(i, collection),
                                                              label = CaloWPLabel)
                if doinclusive:
                    JetSelectionIter = "abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30 && {1}_passesTightLeptVetoID[{0}] > 0".format("?", collection)
                    logging.info("Making inclusive effciency ordered by {0} w/ CSV as tagger".format(collectionName))
                    logging.subinfo("Using collection: {0}".format(collection))
                    CSVPlotBaseObjIter= modules.classes.PlotBase("{1}_csv[{0}]".format("?", collection),
                                                                 "{0} && {1} && ({2})".format(CSVSelection, offlineSelection, JetSelectionIter),
                                                                 "1",
                                                                 [20,0,1],
                                                                 modules.utils.getAxisTitle("csv", 0, collectionName.lower(), inclusive = True ),
                                                                 LegendPosition = [0.1,0.6,0.4,0.76])
                    #CSVPlotBaseObjIter.color = WPColors[0]
                    onlysamples = []
                    
                    for sampleStuff in samples:
                        sample, name, label = sampleStuff
                        onlysamples.append(sample)
                        if not (doMC and doData):
                            modules.effPlots.makeEffSumPlot(CSVPlotBaseObjIter, sample,
                                                            "pfJets_csv[{2}_matchPF[{1}]] >= {0}".format(WP, "?", collection), nInclusiveIter,
                                                            basepaths+"CSV/{3}/{4}Eff_{2}_Jet{0}_pfWP_{1}_CSV_order{3}".format("incl", WP, name, collectionName, fileprefix),
                                                            addSel = "{1}_matchPF[{0}] >= 0".format("?", collection),
                                                            label = [label,WPLabel])
                            modules.effPlots.makeEffSumPlot(CSVPlotBaseObjIter, sample,
                                                            "caloJets_csv[{2}_matchCalo[{1}]] >= {0}".format(WP, "?", collection), nInclusiveIter,
                                                            basepaths+"CSV/{3}/{4}Eff_{2}_Jet{0}_caloWP_{1}_CSV_order{3}".format("incl", WP, name, collectionName, fileprefix),
                                                            addSel = "{1}_matchCalo[{0}] >= 0".format("?", collection),
                                                            label = [label,CaloWPLabel])
                            
                    if doMC and doData:
                        modules.effPlots.makeEffSummSCompPlot(CSVPlotBaseObjIter, onlysamples,
                                                              "pfJets_csv[{2}_matchPF[{1}]] >= {0}".format(WP, "?", collection), nInclusiveIter,
                                                              basepaths+"CSV/{2}/{3}Eff_DataMC_Jet{0}_pfWP_{1}_CSV_order{2}".format("incl", WP, collectionName, fileprefix),
                                                              addSel = "{1}_matchPF[{0}] >= 0".format("?", collection),
                                                              label = WPLabel)
                        modules.effPlots.makeEffSummSCompPlot(CSVPlotBaseObjIter, onlysamples,
                                                              "caloJets_csv[{2}_matchCalo[{1}]] >= {0}".format(WP, "?", collection), nInclusiveIter,
                                                              basepaths+"CSV/{2}/{3}Eff_DataMC_Jet{0}_caloWP_{1}_CSV_order{2}".format("incl", WP, collectionName, fileprefix),
                                                              addSel = "{1}_matchCalo[{0}] >= 0".format("?", collection),
                                                              label = CaloWPLabel)

                if doCross:
                    if dosplit:
                        pass
                    if doinclusive:
                        if looseSel:
                            JetSelectionIter = "{1}_deepcsv[{0}] >= 0 && abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30".format("?", collection)
                        else:
                            JetSelectionIter = "{1}_deepcsv[{0}] >= 0 && abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30 && {1}_passesTightLeptVetoID[{0}] > 0".format("?", collection)
                        logging.info("Making inclusive effciency ordered by {0} w/ DeepCSV as tagger".format(collectionName))
                        logging.subinfo("Using collection: {0}".format(collection))
                        DeepCSVPlotBaseIter = modules.classes.PlotBase("{1}_deepcsv[{0}]".format("?", collection),
                                                                       "{0} && {1} && ({2})".format(CSVSelection, offlineSelection, JetSelectionIter),
                                                                       "1",
                                                                       [20,0,1],
                                                                       modules.utils.getAxisTitle("deepcsv", 0, collectionName.lower(), inclusive = True),
                                                                       LegendPosition = [0.1,0.6,0.4,0.76])
                        onlysamples = []
                        for sampleStuff in samples:
                            sample, name, label = sampleStuff
                            onlysamples.append(sample)

                        if doMC and doData:
                            modules.effPlots.makeEffSummSCompPlot(DeepCSVPlotBaseIter, onlysamples,
                                                                  "pfJets_csv[{2}_matchPF[{1}]] >= {0}".format(WP, "?", collection), nInclusiveIter,
                                                                  basepaths+"CSV/{2}/{3}Eff_DataMC_Jet{0}_pfWP_{1}_CSV_order{2}".format("cross", WP, collectionName, fileprefix),
                                                                  addSel = "{1}_matchPF[{0}] >= 0".format("?", collection),
                                                                  label = WPLabel)
                            modules.effPlots.makeEffSummSCompPlot(DeepCSVPlotBaseIter, onlysamples,
                                                                  "caloJets_csv[{2}_matchCalo[{1}]] >= {0}".format(WP, "?", collection), nInclusiveIter,
                                                                  basepaths+"CSV/{2}/{3}Eff_DataMC_Jet{0}_caloWP_{1}_CSV_order{2}".format("cross", WP, collectionName, fileprefix),
                                                                  addSel = "{1}_matchCalo[{0}] >= 0".format("?", collection),
                                                                  label = CaloWPLabel)

        if compWPs:
            logging.info("Makeing CSV WP comparison")
            for collectionName, collection in collections:
                #JetSelectionIter = "abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30".format("?", collection)
                if looseSel:
                    JetSelectionIter = "abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30".format("?", collection)
                else:
                    JetSelectionIter = "abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30 && {1}_passesTightLeptVetoID[{0}] > 0".format("?", collection)
                logging.info("Making inclusive  WP comparison ordered by {0} w/ CSV as tagger".format(collectionName))
                logging.subinfo("Using collection: {0}".format(collection))
                CSVPlotBaseObjIter= modules.classes.PlotBase("{1}_csv[{0}]".format("?", collection),
                                                             "{0} && {1} && ({2})".format(CSVSelection, offlineSelection, JetSelectionIter),
                                                             "1",
                                                             [20,0,1],
                                                             modules.utils.getAxisTitle("csv", 0, collectionName.lower(), inclusive = True ),
                                                             LegendPosition = [0.1,0.6,0.4,0.76])
                
                for sampleStuff in samples:
                    sample, name, label = sampleStuff
                    logging.info("Plotting sample {0}".format(name))
                    modules.effPlots.makeSumWPComp(CSVPlotBaseObjIter, sample,
                                                   "pfJets_csv[{1}_matchPF[{0}]]".format("?", collection), nInclusiveIter, CSVWPs, 
                                                   basepaths+"CSV/{3}/{4}Eff_{2}_Jet{0}_pfWPComp_{1}_CSV_order{3}".format("incl", WP, name, collectionName, fileprefix),
                                                   addSel = "{1}_matchPF[{0}] >= 0".format("?", collection))
                    modules.effPlots.makeSumWPComp(CSVPlotBaseObjIter, sample,
                                                   "caloJets_csv[{1}_matchCalo[{0}]]".format("?", collection), nInclusiveIter, CSVWPs, 
                                                   basepaths+"CSV/{3}/{4}Eff_{2}_Jet{0}_caloWPComp_{1}_CSV_order{3}".format("incl", WP, name, collectionName, fileprefix),
                                                   addSel = "{1}_matchCalo[{0}] >= 0".format("?", collection))

                    
                


                    
    if doDeepCSV:
        logging.info("Processing plots for DeepCSV")
        DeepCSVPlotBaseObjs = {} 

        collections = []
        if ptordered:
            collections.append( ("pT", "offJets") )
            logging.debug("Adding {1} to collecton as ordered by {0}".format("ptOrdered", "cleanJets"))
        if csvordered:                
            collections.append( ("DeepCSV", "cleanDeepCSVJets") )
            logging.debug("Adding {1} to collecton as ordered by {0}".format("csvOrdered", "cleanDeepCSVJets"))

            
        for WP in DeepCSVWPs:
            WPLabel = getLabel("PF WP: {0}".format(WP), 0.7, "under")
            CaloWPLabel = getLabel("Calo WP: {0}".format(WP), 0.7, "under")
            logging.info("Using WP: {0}".format(WP))
            for collectionName, collection in collections:

                if dosplit:
                    for i in range(nSplitIter):
                        if looseSel:
                            JetSelection = "{1}_deepcsv[{0}] >= 0 && abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30".format(i, collection)
                        else:
                            JetSelection = "{1}_deepcsv[{0}] >= 0 && abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30 && {1}_passesTightLeptVetoID[{0}] > 0".format(i, collection)
                        logging.info("Making effciency for Jet {0} ordered by {1} w/ DeepCSV as tagger".format(i, collectionName))
                        logging.subinfo("Using collection: {0}".format(collection))
                        DeepCSVPlotBaseObjs[i] = modules.classes.PlotBase("{1}_deepcsv[{0}]".format(i, collection),
                                                                          "{0} && {1} && ({2})".format(CSVSelection, offlineSelection, JetSelection),
                                                                          "1",
                                                                          [20,0,1],
                                                                          modules.utils.getAxisTitle("deepcsv", i, collectionName.lower()),
                                                                          LegendPosition = [0.1,0.6,0.4,0.76])




                        DeepCSVPlotBaseObjs[i].color = WPColors[i]
                        onlysamples = []
                        for sampleStuff in samples:
                            sample, name, label = sampleStuff
                            onlysamples.append(sample)
                            if not (doMC and doData): 
                                modules.effPlots.makeEffPlot(DeepCSVPlotBaseObjs[i], sample,
                                                             "(pfJets_deepcsv[{2}_matchPF[{1}]]) >= {0}".format(WP, i, collection),
                                                             basepaths+"DeepCSV/{3}/{4}Eff_{2}_Jet{0}_pfWP_{1}_DeepCSV_order{3}".format(i, WP, name, collectionName, fileprefix),
                                                             addSel = "{1}_matchPF[{0}] >= 0".format(i, collection),
                                                             label = [label,WPLabel])
                                modules.effPlots.makeEffPlot(DeepCSVPlotBaseObjs[i], sample,
                                                             "(caloJets_deepcsv[{2}_matchCalo[{1}]]) >= {0}".format(WP, i, collection),
                                                             basepaths+"DeepCSV/{3}/{4}Eff_{2}_Jet{0}_caloWP_{1}_DeepCSV_order{3}".format(i, WP, name, collectionName, fileprefix),
                                                             addSel = "{1}_matchCalo[{0}] >= 0".format(i, collection),
                                                             label = [label,CaloWPLabel])

                        if doMC and doData:
                            modules.effPlots.makeEffSCompPlot(DeepCSVPlotBaseObjs[i], onlysamples,
                                                              "(pfJets_deepcsv[{2}_matchPF[{1}]]) >= {0}".format(WP, i, collection),
                                                              basepaths+"DeepCSV/{2}/{3}Eff_DataMC_Jet{0}_pfWP_{1}_DeepCSV_order{2}".format(i, WP, collectionName, fileprefix),
                                                              addSel = "{1}_matchPF[{0}] >= 0".format(i, collection),
                                                              label = WPLabel)
                            modules.effPlots.makeEffSCompPlot(DeepCSVPlotBaseObjs[i], onlysamples,
                                                              "(caloJets_deepcsv[{2}_matchCalo[{1}]]) >= {0}".format(WP, i, collection),
                                                              basepaths+"DeepCSV/{2}/{3}Eff_DataMC_Jet{0}_caloWP_{1}_DeepCSV_order{2}".format(i, WP, collectionName, fileprefix),
                                                              addSel = "{1}_matchCalo[{0}] >= 0".format(i, collection),
                                                              label = CaloWPLabel)
                if doinclusive:
                    if looseSel:
                        JetSelectionIter = "{1}_deepcsv[{0}] >= 0 && abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30".format("?", collection)
                    else:
                        JetSelectionIter = "{1}_deepcsv[{0}] >= 0 && abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30 && {1}_passesTightLeptVetoID[{0}] > 0".format("?", collection)
                    logging.info("Making inclusive effciency ordered by {0} w/ DeepCSV as tagger".format(collectionName))
                    logging.subinfo("Using collection: {0}".format(collection))
                    DeepCSVPlotBaseIter = modules.classes.PlotBase("{1}_deepcsv[{0}]".format("?", collection),
                                                                   "{0} && {1} && ({2})".format(CSVSelection, offlineSelection, JetSelectionIter),
                                                                   "1",
                                                                   [20,0,1],
                                                                   modules.utils.getAxisTitle("deepcsv", 0, collectionName.lower(), inclusive = True),
                                                                   LegendPosition = [0.1,0.6,0.4,0.76])




                    onlysamples = []
                    for sampleStuff in samples:
                        sample, name, label = sampleStuff
                        onlysamples.append(sample)
                        if not (doMC and doData): 
                            modules.effPlots.makeEffSumPlot(DeepCSVPlotBaseIter, sample,
                                                            "(pfJets_deepcsv[{2}_matchPF[{1}]]) >= {0}".format(WP, "?", collection), nInclusiveIter,
                                                            basepaths+"DeepCSV/{3}/{4}Eff_{2}_Jet{0}_pfWP_{1}_DeepCSV_order{3}".format("incl", WP, name, collectionName, fileprefix),
                                                            addSel = "{1}_matchPF[{0}] >= 0".format("?", collection),
                                                            label = [label,WPLabel])
                            modules.effPlots.makeEffSumPlot(DeepCSVPlotBaseIter, sample,
                                                            "(caloJets_deepcsv[{2}_matchCalo[{1}]]) >= {0}".format(WP, "?", collection), nInclusiveIter,
                                                            basepaths+"DeepCSV/{3}/{4}Eff_{2}_Jet{0}_caloWP_{1}_DeepCSV_order{3}".format("incl", WP, name, collectionName, fileprefix),
                                                            addSel = "{1}_matchCalo[{0}] >= 0".format("?", collection),
                                                            label = [label,CaloWPLabel])

                    if doMC and doData:
                        modules.effPlots.makeEffSummSCompPlot(DeepCSVPlotBaseIter, onlysamples,
                                                              "(pfJets_deepcsv[{2}_matchPF[{1}]]) >= {0} && {2}_matchPF[{1}] >= 0".format(WP, "?", collection), nInclusiveIter,
                                                              basepaths+"DeepCSV/{2}/{3}Eff_DataMC_Jet{0}_pfWP_{1}_DeepCSV_order{2}".format("incl", WP, collectionName, fileprefix),
                                                              addSel = "{1}_matchPF[{0}] >= 0".format("?", collection),
                                                              label = WPLabel)
                        modules.effPlots.makeEffSummSCompPlot(DeepCSVPlotBaseIter, onlysamples,
                                                              "(caloJets_deepcsv[{2}_matchCalo[{1}]]) >= {0}".format(WP, "?", collection), nInclusiveIter,
                                                              basepaths+"DeepCSV/{2}/{3}Eff_DataMC_Jet{0}_caloWP_{1}_DeepCSV_order{2}".format("incl", WP, collectionName, fileprefix),
                                                              addSel = "{1}_matchCalo[{0}] >= 0".format("?", collection),
                                                              label = CaloWPLabel)

        if compWPs:
            logging.info("Makeing DeepCSV WP comparison")
            for collectionName, collection in collections:
                if looseSel:
                    #JetSelectionIter = "abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30".format("?", collection)
                    JetSelectionIter = "{1}_pt[{0}] > 0".format("?", collection)
                else:
                    JetSelectionIter = "{1}_deepcsv[{0}] >= 0 && abs({1}_eta[{0}]) < 2.4 && {1}_pt[{0}] > 30 && {1}_passesTightLeptVetoID[{0}] > 0".format("?", collection)
                logging.info("Making inclusive  WP comparison ordered by {0} w/ DeepCSV as tagger".format(collectionName))
                logging.subinfo("Using collection: {0}".format(collection))
                DeepCSVPlotBaseIter = modules.classes.PlotBase("{1}_deepcsv[{0}]".format("?", collection),
                                                               "{0} && {1} && ({2})".format(CSVSelection, offlineSelection, JetSelectionIter),
                                                               "1",
                                                               [25,0,1],
                                                               modules.utils.getAxisTitle("deepcsv", 0, collectionName.lower(), inclusive = True),
                                                               LegendPosition = [0.1,0.6,0.4,0.76])

                
                for sampleStuff in samples:
                    sample, name, label = sampleStuff
                    logging.info("Plotting sample {0}".format(name))
                    modules.effPlots.makeSumWPComp(DeepCSVPlotBaseIter, sample,
                                                   "pfJets_deepcsv[{1}_matchPF[{0}]]".format("?", collection), nInclusiveIter, DeepCSVWPs, 
                                                   basepaths+"DeepCSV/{3}/{4}Eff_{2}_Jet{0}_pfWPComp_{1}_DeepCSV_order{3}".format("incl", WP, name, collectionName, fileprefix),
                                                   #addSel = "pfJets_deepcsv[{1}_matchPF[{0}]] >= 0 && {1}_matchPF[{0}] >= 0 && pfJets_pt[{1}_matchPF[{0}]] > 30 && abs(pfJets_eta[{1}_matchPF[{0}]]) < 2.4".format("?", collection)
                                                   addSel = "{1}_matchPF[{0}] >= 0 && emilSourceValid == 1".format("?", collection), saveGraph = True
                    )
                    """
                    modules.effPlots.makeSumWPComp(DeepCSVPlotBaseIter, sample,
                                                   "caloJets_deepcsv[{1}_matchCalo[{0}]]".format("?", collection), nInclusiveIter, DeepCSVWPs, 
                                                   basepaths+"DeepCSV/{3}/{4}Eff_{2}_Jet{0}_caloWPComp_{1}_DeepCSV_order{3}".format("incl", WP, name, collectionName, fileprefix),
                                                   addSel = "caloJets_deepcsv[{1}_matchCalo[{0}]] >= 0 && {1}_matchCalo[{0}] >= 0 && pfJets_pt[{1}_matchCalo[{0}]] > 30 && abs(pfJets_eta[{1}_matchCalo[{0}]]) < 2.4".format("?", collection),
                                                   #addSel = "caloJets_deepcsv[{1}_matchCalo[{0}]] >= 0".format("?", collection),
                    )

                    """
                        
                            

    logger.info("Runtime: {0:8f}s".format(time.time()-t0))
    logger.info("Closing efficiency turnon calc")
if __name__ == "__main__":
    import argparse
    ##############################################################################################################
    ##############################################################################################################
    # Argument parser definitions:
    argumentparser = argparse.ArgumentParser(
        description='Description'
    )

    argumentparser.add_argument(
        "--logging",
        action = "store",
        help = "Define logging level: CRITICAL - 50, ERROR - 40, WARNING - 30, INFO - 20, DEBUG - 10, NOTSET - 0 \nSet to 0 to activate ROOT root messages",
        type=int,
        default=20
    )
    argumentparser.add_argument(
        "--run",
        action = "store",
        help = "Set Run for measurement. Option CD, E, F, Test",
        type = str,
        choices = ["CD", "E", "F", "Test"]
    )
    argumentparser.add_argument(
        "--mc",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--data",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--csv",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--deepcsv",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--csvWP",
        action = "store",
        help = "CSV WPs that are plotted",
        nargs='+',
        type=str,
        default = ["0.8484"]
    )
    argumentparser.add_argument(
        "--deepcsvWP",
        action = "store",
        help = "DeepCSV WPs that are plotted",
        nargs='+',
        type=str,
        default = ["0.6324"]
    )
    argumentparser.add_argument(
        "--TnP",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--ptordered",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--csvordered",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--inclusive",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--ninclusive",
        action = "store",
        help = "Number of iterations for inclusive efficiencies",
        type=int,
        default = 10,
    )
    argumentparser.add_argument(
        "--split",
        action = "store_true",
        help = "Call without argument!",
    )
    argumentparser.add_argument(
        "--nsplit",
        action = "store",
        help = "Number of iterations for split efficiencies",
        type=int,
        default = 2
    )
    argumentparser.add_argument(
        "--crossTagger",
        action = "store_true",
        help = "Corss tagger plots (only CSV WP with DeepCSV plot for now)",
    )
    argumentparser.add_argument(
        "--compWPs",
        action = "store_true",
        help = "Make plots comparing WPs set by  the --csvWP and deepcsvWP. This plots will be split by Data and MC.",
    )
    argumentparser.add_argument(
        "--looseSel",
        action = "store_true",
        help = "Removing most cuts on trigger, event, etc",
    )
    
    
    

    
    args = argumentparser.parse_args()
    #
    ##############################################################################################################
    ##############################################################################################################

        
    efficiencies(loglev = args.logging, run = args.run, doMC = args.mc, doData = args.data, doCSV = args.csv, doDeepCSV = args.deepcsv, CSVWPs = args.csvWP, DeepCSVWPs = args.deepcsvWP, ptordered = args.ptordered, csvordered = args.csvordered, doinclusive = args.inclusive, nInclusiveIter = args.ninclusive, dosplit = args.split, nSplitIter = args.nsplit, doCross = args.crossTagger, compWPs = args.compWPs, looseSel=  args.looseSel)

    logging.info("Exiting efficiencies.py")
