# -*- coding: utf-8 -*-
# SPDX-License-Identifier: EUPL-1.2
#  
#  Copyright (c) 2022-2024  Marc van der Sluys - Nikhef/Utrecht University - marc.vandersluys.nl
#  
#  This file is part of the sluyspy Python package:
#  Marc van der Sluys' personal Python modules.
#  See: https://github.com/MarcvdSluys/sluyspy
#  
#  This is free software: you can redistribute it and/or modify it under the terms of the European Union
#  Public Licence 1.2 (EUPL 1.2).  This software is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#  PURPOSE.  See the EU Public Licence for more details.  You should have received a copy of the European
#  Union Public Licence along with this code.  If not, see <https://www.eupl.eu/1.2/en/>.


"""Machine-learning functions for the sluyspy package"""


def stats_from_conf_mat(df):
    """Add common ML statistics to a Pandas DataFrame containing the confusion-matrix elements.
    
    Parameters:
      df (pd.df):  Pandas DataFrame containing the confusion-matrix elements in the following columns:
    
        - tp:  Number or fraction of true positives.
        - tn:  Number or fraction of true negatives.
        - fp:  Number or fraction of false positives.
        - fn:  Number or fraction of false negatives.
    
    Returns:
      (pd.df):  Pandas DataFrame containing different machine-learning statistics, with new columns:
    
        - p:  Total number of actual positive cases in the data.
        - n:  Total number of actual negaitive cases in the data.
    
        - tpr:  TPR: true positive rate (sensitivity):  TPR = TP/P = TP/(TP+FN).
        - tnr:  TNR: true negative rate (specificity):  TNR = TN/N = TN/(TN+FP).
        - fpr:  FPR: false positive rate (fall out):    FPR = FP/N = FP/(FP+TN).
        - fnr:  FNR: false negative rate (miss rate):   FNR = FN/P = FN/(FN+TP).
    
        - ppv:  PPV - positive predictive value - precision: PPV = TP/(TP+FP).
        - npv:  NPV - negative predictive value:             NPV = TN/(TN+FN).
        - fdr:  FDR - false discovery rate:                  FDR = FP/(TP+FP).
        - for:  FOR - false omission rate:                   FOR = FN/(TN+FN).
    
        - acc:  accuracy: fraction of true predictions:  ACC = (TP+TN)/(P+N).
        - f1:  F1 score: harmonic mean of PPV and TPR:   F1  = PPV*TPR/(PPV+TPR).
    """
    
    tp = df.tp
    tn = df.tn
    fp = df.fp
    fn = df.fn
    
    df['p']   = fn + tp                  # Total number of actual positive cases in the data
    df['n']   = fp + tn                  # Total number of actual negaitive cases in the data
    
    df['tpr'] = tp/(tp+fn)               # TPR: true positive rate (sensitivity): TPR = TP/P
    df['tnr'] = tn/(tn+fp)               # TNR: true negative rate (specificity): TNR = TN/N
    
    df['fpr'] = fp/(fp+tn)               # FPR: false positive rate (fall out): FPR = FP/N
    df['fnr'] = fn/(fn+tp)               # FNR: false negative rate (miss rate): FNR = FN/P
    
    df['ppv'] = tp/(tp+fp)               # PPV - positive predictive value - precision: PPV = TP/(TP+FP)
    df['npv'] = tn/(tn+fn)               # NPV - negative predictive value: NPV = TN/(TN+FN)
    
    df['fdr'] = fp/(tp+fp)               # FDR - false discovery rate: FDR = FP/(TP+FP)
    df['for'] = fn/(tn+fn)               # FOR - false omission rate: FOR = FN/(TN+FN)
    
    df['acc'] = (tp+tn)/(tp+tn+fp+fn)    # accuracy: fraction of true predictions: ACC = (TP+TN)/(P+N)
    df['f1']  = (2 * tp)/(2*tp + fp+fn)  # F1 score: harmonic mean of PPV and TPR: F1 = PPV*TPR/(PPV+TPR)
    
    return df


