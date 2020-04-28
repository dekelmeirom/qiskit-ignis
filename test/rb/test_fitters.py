# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Test the fitters
"""

import os
import unittest
from test.utils import *

import numpy as np

from qiskit.ignis.verification.randomized_benchmarking import \
    RBFitter, InterleavedRBFitter, PurityRBFitter, CNOTDihedralRBFitter


class TestFitters(unittest.TestCase):
    """ Test the fitters """

    def compare_results_and_excpected(self, data, expected_data, tst_index):
        """ utility function to compare results """
        data_keys = data[0].keys()
        for i in range(len(expected_data)):
            for key in data_keys:
                if expected_data[i][key] is None:
                    self.assertIsNone(data[i][key], 'Incorrect ' + str(key) + ' in test no. ' + str(tst_index))
                else:
                    # check if the zip function is needed
                    if isinstance(data[i][key], np.ndarray):
                        self.assertTrue(all(np.isclose(a, b) for a, b in
                                            zip(data[i][key], expected_data[i][key])),
                                        'Incorrect ' + str(key) + ' in test no. ' + str(tst_index))
                    else:
                        self.assertTrue(np.isclose(data[i][key], expected_data[i][key]),
                                        'Incorrect ' + str(key) + ' in test no. ' + str(tst_index))


    def test_fitters(self):
        """ Test the fitters """

        # Use json results files
        tests_settings = [
            {
                'rb_opts': {
                    'xdata': np.array([[1, 21, 41, 61, 81, 101, 121, 141,
                                        161, 181],
                                       [2, 42, 82, 122, 162, 202, 242, 282,
                                        322, 362]]),
                    'rb_pattern': [[0, 1], [2]],
                    'shots': 1024},
                'results_file': os.path.join(os.path.dirname(__file__),
                                             'test_fitter_results_1.json')
            },
            {
                'rb_opts': {
                    'xdata': np.array([[1, 21, 41, 61, 81, 101, 121, 141, 161,
                                        181]]),
                    'rb_pattern': [[0]],
                    'shots': 1024},
                'results_file': os.path.join(os.path.dirname(__file__),
                                             'test_fitter_results_2.json')
            }

        ]
        tests_expected_results = [
            {
                'ydata': [{
                    'mean': np.array([0.96367187, 0.73457031,
                                      0.58066406, 0.4828125,
                                      0.41035156, 0.34902344,
                                      0.31210938, 0.2765625,
                                      0.29453125, 0.27695313]),
                    'std': np.array([0.01013745, 0.0060955, 0.00678272,
                                     0.01746491, 0.02015981, 0.02184184,
                                     0.02340167, 0.02360293, 0.00874773,
                                     0.01308156])}, {
                    'mean': np.array([0.98925781,
                                      0.87734375, 0.78125,
                                      0.73066406,
                                      0.68496094,
                                      0.64296875,
                                      0.59238281,
                                      0.57421875,
                                      0.56074219,
                                      0.54980469]),
                    'std': np.array(
                        [0.00276214, 0.01602991,
                         0.00768946, 0.01413015,
                         0.00820777, 0.01441348,
                         0.01272682, 0.01031649,
                         0.02103036, 0.01224408])}],
                'fit': [{
                    'params': np.array([0.71936804, 0.98062119,
                                        0.25803749]),
                    'params_err': np.array([0.0065886, 0.00046714,
                                            0.00556488]),
                    'epc': 0.014534104912075935,
                    'epc_err': 0.0003572769714798349},
                    {'params': np.array([0.49507094, 0.99354093,
                                         0.50027262]),
                     'params_err': np.array([0.0146191, 0.0004157,
                                             0.01487439]),
                     'epc': 0.0032295343343508587,
                     'epc_err': 0.00020920242080699664}]
            },
            {
                'ydata': [{'mean': np.array([0.99199219, 0.93867188,
                                             0.87871094, 0.83945313,
                                             0.79335937, 0.74785156,
                                             0.73613281, 0.69414062,
                                             0.67460937, 0.65664062]),
                           'std': np.array([0.00567416, 0.00791919,
                                            0.01523437, 0.01462368,
                                            0.01189002, 0.01445049,
                                            0.00292317, 0.00317345,
                                            0.00406888,
                                            0.01504794])}],
                'fit': [{'params': np.array([0.59599995, 0.99518211,
                                             0.39866989]),
                         'params_err': np.array([0.08843152, 0.00107311,
                                                 0.09074325]),
                         'epc': 0.0024089464034862673,
                         'epc_err': 0.0005391508310961153}]}
        ]

        for tst_index, tst_expected_results in enumerate(tests_expected_results):
            results_list = load_results_from_json(tests_settings[tst_index]['results_file'])

            # RBFitter class
            rb_fit = RBFitter(results_list[0], tests_settings[tst_index]['rb_opts']['xdata'],
                              tests_settings[tst_index]['rb_opts']['rb_pattern'])

            # add the seeds in reverse order
            for seedind in range(len(results_list)-1, 0, -1):
                rb_fit.add_data([results_list[seedind]])

            ydata = rb_fit.ydata
            fit = rb_fit.fit

            self.compare_results_and_excpected(ydata, tst_expected_results['ydata'], tst_index)
            self.compare_results_and_excpected(fit, tst_expected_results['fit'], tst_index)


    def test_interleaved_fitters(self):
        """ Test the interleaved fitters """

        # Use json results files
        tests_settings = [
            {
                'rb_opts': {
                    'xdata': np.array([[1, 11, 21, 31, 41,
                                        51, 61, 71, 81, 91],
                                       [3, 33, 63, 93, 123,
                                        153, 183, 213, 243, 273]]),
                    'rb_pattern': [[0, 2], [1]],
                    'shots': 200},
                'original_results_file':
                    os.path.join(
                        os.path.dirname(__file__),
                        'test_fitter_original_results.json'),
                'interleaved_results_file':
                    os.path.join(
                        os.path.dirname(__file__),
                        'test_fitter_interleaved_results.json')
            }]

        tests_expected_results = [
            {
                'original_ydata':
                    [{'mean': np.array([0.9775, 0.79, 0.66,
                                        0.5775, 0.5075, 0.4825,
                                        0.4075, 0.3825,
                                        0.3925, 0.325]),
                      'std': np.array([0.0125, 0.02, 0.01,
                                       0.0125, 0.0025,
                                       0.0125, 0.0225, 0.0325,
                                       0.0425, 0.])},
                     {'mean': np.array([0.985, 0.9425, 0.8875,
                                        0.8225, 0.775, 0.7875,
                                        0.7325, 0.705,
                                        0.69, 0.6175]),
                      'std': np.array([0.005, 0.0125, 0.0025,
                                       0.0025, 0.015, 0.0125,
                                       0.0075, 0.01,
                                       0.02, 0.0375])}],
                'interleaved_ydata':
                    [{'mean': np.array([0.955, 0.7425, 0.635,
                                        0.4875, 0.44, 0.3625,
                                        0.3575, 0.2875,
                                        0.2975, 0.3075]),
                      'std': np.array([0., 0.0025, 0.015,
                                       0.0075, 0.055,
                                       0.0075, 0.0075, 0.0025,
                                       0.0025, 0.0075])},
                     {'mean': np.array([0.9775, 0.85, 0.77,
                                        0.7775, 0.6325,
                                        0.615, 0.64, 0.6125,
                                        0.535, 0.55]),
                      'std': np.array([0.0075, 0.005, 0.01,
                                       0.0025, 0.0175, 0.005,
                                       0.01, 0.0075,
                                       0.01, 0.005])}],
                'joint_fit': [
                    {'alpha': 0.9707393978697902,
                     'alpha_err': 0.0028343593038762326,
                     'alpha_c': 0.9661036105117012,
                     'alpha_c_err': 0.003096602375173838,
                     'epc_est': 0.003581641505636224,
                     'epc_est_err': 0.0032362911276774308,
                     'systematic_err': 0.04030926168967841,
                     'systematic_err_L': -0.03672762018404219,
                     'systematic_err_R': 0.043890903195314634},
                    {'alpha': 0.9953124384370953,
                     'alpha_err': 0.0014841466685991903,
                     'alpha_c': 0.9955519189829325,
                     'alpha_c_err': 0.002194868426034655,
                     'epc_est': -0.00012030420629183247,
                     'epc_est_err': 0.001331116936065506,
                     'systematic_err': 0.004807865769196562,
                     'systematic_err_L': -0.0049281699754883945,
                     'systematic_err_R': 0.00468756156290473}]
            }
            ]

        for tst_index, tst_expected_results in enumerate(tests_expected_results):
            original_result_list = load_results_from_json(tests_settings[tst_index]['original_results_file'])
            interleaved_result_list = load_results_from_json(tests_settings[tst_index]['interleaved_results_file'])


            # InterleavedRBFitter class
            joint_rb_fit = InterleavedRBFitter(
                original_result_list, interleaved_result_list,
                tests_settings[tst_index]['rb_opts']['xdata'], tests_settings[tst_index]['rb_opts']['rb_pattern'])

            joint_fit = joint_rb_fit.fit_int
            ydata_original = joint_rb_fit.ydata[0]
            ydata_interleaved = joint_rb_fit.ydata[1]

            self.compare_results_and_excpected(ydata_original, tst_expected_results['original_ydata'], tst_index)
            self.compare_results_and_excpected(ydata_interleaved, tst_expected_results['interleaved_ydata'], tst_index)
            self.compare_results_and_excpected(joint_fit, tst_expected_results['joint_fit'], tst_index)

    def test_purity_fitters(self):
        """ Test the purity fitters """

        # Use json results files
        tests_settings = [
            {
                'npurity': 9,
                'rb_opts': {
                    'xdata': np.array([[1, 21, 41, 61, 81, 101, 121,
                                        141, 161, 181],
                                       [1, 21, 41, 61, 81, 101, 121,
                                        141, 161, 181]]),
                    'rb_pattern': [[0, 1], [2, 3]],
                    'shots': 200},
                'results_file': os.path.join(
                    os.path.dirname(__file__),
                    'test_fitter_purity_results.json')
            },
            {
                'npurity': 9,
                'rb_opts': {
                    'xdata': np.array([[1, 21, 41, 61, 81, 101, 121,
                                        141, 161, 181],
                                       [1, 21, 41, 61, 81, 101, 121,
                                        141, 161, 181]]),
                    'rb_pattern': [[0, 1], [2, 3]],
                    'shots': 200},
                'results_file': os.path.join(
                    os.path.dirname(__file__),
                    'test_fitter_coherent_purity_results.json')
            }
        ]

        tests_expected_results = [
            {
                'ydata':
                    [{'mean': np.array([0.92534849, 0.51309098,
                                        0.3622178, 0.29969053,
                                        0.26635693, 0.25874519,
                                        0.25534863, 0.25298818,
                                        0.25352012, 0.2523394]),
                      'std': np.array([0.01314403, 0.00393961,
                                       0.01189933, 0.00936296,
                                       0.00149143, 0.00248324,
                                       0.00162298, 0.00047547,
                                       0.00146307, 0.00104081])},
                     {'mean': np.array([0.92369652, 0.52535891,
                                        0.36284821, 0.28978369,
                                        0.26764608, 0.26141492,
                                        0.25365907, 0.25399547,
                                        0.25308856, 0.25243922]),
                      'std': np.array([0.01263948, 0.0139054,
                                       0.00774744, 0.00514974,
                                       0.00110454, 0.00185583,
                                       0.00103562, 0.00108479,
                                       0.00032715, 0.00067735])}],
                'fit':
                    [{'params': np.array([0.70657607, 0.97656138,
                                          0.25222978]),
                      'params_err': np.array([0.00783723, 0.00028377,
                                              0.00026126]),
                      'epc': 0.034745905818288264,
                      'epc_err': 0.0004410703043924575,
                      'pepc': 0.017578966279446773,
                      'pepc_err': 0.00021793530767170674},
                     {'params': np.array([0.70689622, 0.97678485,
                                          0.25258977]),
                      'params_err': np.array([0.01243358, 0.00037419,
                                              0.00027745]),
                      'epc': 0.03441852175571036,
                      'epc_err': 0.0005814179624217788,
                      'pepc': 0.017411364623216907,
                      'pepc_err': 0.00028731473935779276}]
            },
            {
                'ydata':
                    [{'mean': np.array([1.03547598, 1.00945614,
                                        0.9874103, 0.99794296,
                                        0.98926947, 0.98898662,
                                        0.9908188, 1.04339706,
                                        1.02311855, 1.02636139]),
                      'std': np.array([0.00349072, 0.05013115,
                                       0.01657108, 0.03048466,
                                       0.03496286, 0.02572242,
                                       0.03661921, 0.02406485,
                                       0.04192087, 0.05903551])},
                     {'mean': np.array([1.04122543, 0.98568824,
                                        0.98702183, 1.00184751,
                                        1.02116973, 0.98867042,
                                        1.06620605, 1.11332653,
                                        1.04427034, 1.0687145]),
                      'std': np.array([0.00519259, 0.02815319,
                                       0.06940576, 0.0232619,
                                       0.0442728, 0.05649533,
                                       0.05882039, 0.13732109,
                                       0.06189085, 0.0890274])}],
                'fit':
                    [{'params': np.array([0.04050766, 0.91275946,
                                          1.00172827]),
                      'params_err': np.array([0.09520572, 1.04827404,
                                              0.00820391]),
                      'epc': 0.12515262778294844,
                      'epc_err': 1.8031488429069056,
                      'pepc': 0.06543040590251992,
                      'pepc_err': 0.8613501881980827},
                     {'params': np.array([0.07347761, 0.68002963,
                                          1.00724559]),
                      'params_err': np.array([1.20673822e+04,
                                              4.60490058e+04,
                                              1.15476367e-02]),
                      'epc': 0.4031697796194298,
                      'epc_err': 123174.20450564621,
                      'pepc': 0.23997777961599784,
                      'pepc_err': 50787.13189860349}]
            }
        ]

        for tst_index, tst_expected_results in enumerate(tests_expected_results[0:1]):
            purity_result_list = load_results_from_json(tests_settings[tst_index]['results_file'])

            # PurityRBFitter class
            rbfit_purity = PurityRBFitter(purity_result_list,
                                          tests_settings[tst_index]['npurity'],
                                          tests_settings[tst_index]['rb_opts']['xdata'],
                                          tests_settings[tst_index]['rb_opts']['rb_pattern'])

            ydata = rbfit_purity.ydata
            fit = rbfit_purity.fit

            self.compare_results_and_excpected(ydata, tst_expected_results['ydata'], tst_index)
            self.compare_results_and_excpected(fit, tst_expected_results['fit'], tst_index)

    def test_cnotdihedral_fitters(self):
        """ Test the non-clifford cnot-dihedral CNOT-Dihedral
        fitters """

        # Use json results files
        tests_settings = [
            {
                'rb_opts': {
                    'xdata': np.array([[1, 21, 41, 61,
                                        81, 101, 121, 141,
                                        161, 181],
                                       [3, 63, 123, 183,
                                        243, 303, 363, 423,
                                        483, 543]]),
                    'rb_pattern': [[0, 2], [1]],
                    'shots': 200},
                'cnotdihedral_X_results_file':
                    os.path.join(
                        os.path.dirname(__file__),
                        'test_fitter_cnotdihedral_X_results.json'),
                'cnotdihedral_Z_results_file':
                    os.path.join(
                        os.path.dirname(__file__),
                        'test_fitter_cnotdihedral_Z_results.json')
            }
        ]

        tests_expected_results = [
            {
                'cnotdihedral_X_ydata':
                    [{'mean': np.array([0.961, 0.72, 0.565,
                                        0.462, 0.353, 0.34,
                                        0.303, 0.301, 0.28,
                                        0.233]),
                      'std': np.array([0.00969536, 0.01048809,
                                       0.03271085, 0.03385262,
                                       0.02839014, 0.02167948,
                                       0.03919184, 0.03152777,
                                       0.02280351, 0.0150333])},
                     {'mean': np.array([0.995, 0.936, 0.894,
                                        0.859, 0.82, 0.78,
                                        0.763, 0.709, 0.695,
                                        0.66]),
                      'std': np.array([0.00547723, 0.02154066,
                                       0.01593738, 0.0174356,
                                       0.03937004, 0.03114482,
                                       0.026, 0.01529706,
                                       0.02387467, 0.02302173])}],
                'cnotdihedral_Z_ydata':
                    [{'mean': np.array([0.97, 0.725, 0.578,
                                        0.462, 0.373, 0.348,
                                        0.32, 0.311, 0.263, 0.268]),
                      'std': np.array([0.01643168, 0.04301163,
                                       0.0256125, 0.03059412,
                                       0.03722902, 0.02063977,
                                       0.01760682, 0.00860233,
                                       0.03026549, 0.02976575])},
                     {'mean': np.array([0.997, 0.953, 0.913, 0.855,
                                        0.806, 0.772, 0.742, 0.7,
                                        0.682, 0.654]),
                      'std': np.array([0.006, 0.01630951, 0.01077033,
                                       0.0083666, 0.02517936,
                                       .02014944, 0.00509902,
                                       0.03193744, 0.00812404,
                                       0.02782086])}],
                'joint_fit': [
                    {'alpha': 0.980236195543166,
                     'alpha_err': 0.0008249166207232896,
                     'epg_est': 0.014822853342625508,
                     'epg_est_err': 0.0006311616203884836},
                    {'alpha': 0.99867758415237,
                     'alpha_err': 0.00018607263163029097,
                     'epg_est': 0.0006612079238150215,
                     'epg_est_err': 9.315951142941721e-05}]
            }
        ]

        for tst_index, tst_expected_results in enumerate(tests_expected_results):
            cnotdihedral_X_result_list = load_results_from_json(tests_settings[tst_index]['cnotdihedral_X_results_file'])
            cnotdihedral_Z_result_list = load_results_from_json(tests_settings[tst_index]['cnotdihedral_Z_results_file'])

            # CNOTDihedralRBFitter class
            joint_rb_fit = CNOTDihedralRBFitter(
                cnotdihedral_Z_result_list, cnotdihedral_X_result_list,
                tests_settings[tst_index]['rb_opts']['xdata'], tests_settings[tst_index]['rb_opts']['rb_pattern'])

            joint_fit = joint_rb_fit.fit_cnotdihedral
            ydata_Z = joint_rb_fit.ydata[0]
            ydata_X = joint_rb_fit.ydata[1]

            self.compare_results_and_excpected(ydata_Z, tst_expected_results['cnotdihedral_Z_ydata'], tst_index)
            self.compare_results_and_excpected(ydata_X, tst_expected_results['cnotdihedral_X_ydata'], tst_index)
            self.compare_results_and_excpected(joint_fit, tst_expected_results['joint_fit'], tst_index)


if __name__ == '__main__':
    unittest.main()
