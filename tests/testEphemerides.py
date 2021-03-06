from __future__ import print_function
import unittest
import os
import numpy as np
import pandas as pd
from astropy.time import Time
from pandas.util.testing import assert_frame_equal
from lsst.sims.movingObjects import Orbits
from lsst.sims.movingObjects import PyOrbEphemerides
from lsst.utils import getPackageDir


try:
    import numexpr
    _has_numexpr = True
except ImportError:
    _has_numexpr = False


@unittest.skipIf(not _has_numexpr, "No numexpr available.")
class TestPyOrbEphemerides(unittest.TestCase):
    def setUp(self):
        self.testdir = os.path.join(getPackageDir('sims_movingObjects'), 'tests/orbits_testdata')
        self.orbits = Orbits()
        self.orbits.readOrbits(os.path.join(self.testdir, 'test_orbitsQ.des'))
        self.orbitsKEP = Orbits()
        self.orbitsKEP.readOrbits(os.path.join(self.testdir, 'test_orbitsA.des'))
        self.ephems = PyOrbEphemerides()
        self.ephems.setOrbits(self.orbits)

    def tearDown(self):
        del self.orbits
        del self.orbitsKEP
        del self.ephems

    def testSetOrbits(self):
        # Test that we can set orbits.
        self.ephems.setOrbits(self.orbits)
        # Test that setting with an empty orbit object fails.
        # (Avoids hard-to-interpret errors from pyoorb).
        with self.assertRaises(ValueError):
            emptyOrb = Orbits()
            empty = pd.DataFrame([], columns=self.orbits.dataCols['KEP'])
            emptyOrb.setOrbits(empty)
            self.ephems.setOrbits(emptyOrb)

    def testConvertToOorbArray(self):
        # Check that orbital elements are converted.
        self.ephems._convertToOorbElem(self.orbits.orbits, self.orbits.orb_format)
        self.assertEqual(len(self.ephems.oorbElem), len(self.orbits))
        self.assertEqual(self.ephems.oorbElem[0][7], 2)
        self.assertEqual(self.ephems.oorbElem[0][9], 3)
        self.assertEqual(self.ephems.oorbElem[0][1], self.orbits.orbits['q'][0])
        # Test that we can convert KEP orbital elements too.
        self.ephems._convertToOorbElem(self.orbitsKEP.orbits, self.orbitsKEP.orb_format)
        self.assertEqual(len(self.ephems.oorbElem), len(self.orbitsKEP))
        self.assertEqual(self.ephems.oorbElem[0][7], 3)
        self.assertEqual(self.ephems.oorbElem[0][1], self.orbitsKEP.orbits['a'][0])

    def testConvertFromOorbArray(self):
        self.ephems._convertToOorbElem(self.orbits.orbits, self.orbits.orb_format)
        newOrbits = Orbits()
        newOrbits.setOrbits(self.ephems.convertFromOorbElem())
        print(self.orbits.orb_format, self.orbits.orbits)
        print(newOrbits.orb_format, newOrbits.orbits)
        self.assertEqual(newOrbits, self.orbits)

    def testConvertTimes(self):
        times = np.arange(49353, 49353 + 10, 0.5)
        ephTimes = self.ephems._convertTimes(times, 'UTC')
        # Check that shape of ephTimes is correct.
        self.assertEqual(ephTimes.shape[0], len(times))
        self.assertEqual(ephTimes.shape[1], 2)
        # Check that 'timescale' for ephTimes is correct.
        self.assertEqual(ephTimes[0][1], 1)
        ephTimes = self.ephems._convertTimes(times, 'TAI')
        self.assertEqual(ephTimes[0][1], 4)

    def testOorbEphemeris(self):
        self.ephems.setOrbits(self.orbits)
        times = np.arange(49353, 49353 + 3, 0.25)
        ephTimes = self.ephems._convertTimes(times)
        oorbEphs = self.ephems._generateOorbEphs(ephTimes, obscode=807)
        # Check that it returned the right sort of array.
        self.assertEqual(oorbEphs.shape, (len(self.ephems.oorbElem), len(times), 14))

    def testEphemeris(self):
        # Calculate and convert ephemerides.
        self.ephems.setOrbits(self.orbits)
        times = np.arange(49353, 49353 + 2, 0.3)
        ephTimes = self.ephems._convertTimes(times)
        oorbEphs = self.ephems._generateOorbEphs(ephTimes, obscode=807)
        # Group by object, and check grouping.
        ephs = self.ephems._convertOorbEphs(oorbEphs, byObject=True)
        self.assertEqual(len(ephs), len(self.orbits))
        # Group by time, and check grouping.
        ephs = self.ephems._convertOorbEphs(oorbEphs, byObject=False)
        self.assertEqual(len(ephs), len(times))
        # And test all-wrapped-up method:
        ephsAll = self.ephems.generateEphemerides(times, obscode=807,
                                                  timeScale='UTC', byObject=False)
        np.testing.assert_equal(ephsAll, ephs)
        # Reset ephems to use KEP Orbits, and calculate new ephemerides.
        self.ephems.setOrbits(self.orbitsKEP)
        oorbEphs = self.ephems._generateOorbEphs(ephTimes, obscode=807)
        ephsKEP = self.ephems._convertOorbEphs(oorbEphs, byObject=True)
        self.assertEqual(len(ephsKEP), len(self.orbitsKEP))
        ephsKEP = self.ephems._convertOorbEphs(oorbEphs, byObject=False)
        self.assertEqual(len(ephsKEP), len(times))
        # Check that ephemerides calculated by each method are almost equal.
        for column in ephs.dtype.names:
            np.testing.assert_allclose(ephs[column], ephsKEP[column], rtol=0, atol=1e-7)
        # And test all-wrapped-up method:
        ephsAllKEP = self.ephems.generateEphemerides(times, obscode=807,
                                                     timeScale='UTC', byObject=False)
        np.testing.assert_equal(ephsAllKEP, ephsKEP)
        # Check that the wrapped method using KEP elements and the wrapped method using COM elements match.
        for column in ephsAll.dtype.names:
            np.testing.assert_allclose(ephsAllKEP[column], ephsAll[column], rtol=0, atol=1e-7)


@unittest.skipIf(not _has_numexpr, "No numexpr available.")
class TestJPLValues(unittest.TestCase):
    """Test the oorb generated RA/Dec values against JPL generated RA/Dec values."""
    def setUp(self):
        # Read orbits.
        self.orbits = Orbits()
        self.jplDir = os.path.join(getPackageDir('sims_movingObjects'), 'tests/jpl_testdata')
        self.orbits.readOrbits(os.path.join(self.jplDir, 'S0_n747.des'), skiprows=1)
        # Read JPL ephems.
        self.jpl = pd.read_table(os.path.join(self.jplDir, '807_n747.txt'), delim_whitespace=True)
        # Add times in TAI and UTC, because.
        t = Time(self.jpl['epoch_mjd'], format='mjd', scale='utc')
        self.jpl['mjdTAI'] = t.tai.mjd
        self.jpl['mjdUTC'] = t.utc.mjd

    def tearDown(self):
        del self.orbits
        del self.jpl

    def testRADec(self):
        # We won't compare Vmag, because this also needs information on trailing losses.
        times = self.jpl['mjdUTC'].unique()
        deltaRA = np.zeros(len(times), float)
        deltaDec = np.zeros(len(times), float)
        for i, t in enumerate(times):
            # Find the JPL objIds visible at this time.
            j = self.jpl.query('mjdUTC == @t').sort_values('objId')
            # Set the ephems, using the objects seen at this time.
            suborbits = self.orbits.orbits.query('objId in @j.objId').sort_values('objId')
            subOrbits = Orbits()
            subOrbits.setOrbits(suborbits)
            ephems = PyOrbEphemerides()
            ephems.setOrbits(subOrbits)
            ephs = ephems.generateEphemerides([t], timeScale='UTC', obscode=807, byObject=False)
            deltaRA[i] = np.abs(ephs['ra'] - j['ra_deg'].as_matrix()).max()
            deltaDec[i] = np.abs(ephs['dec'] - j['dec_deg'].as_matrix()).max()
        # Convert to mas
        deltaRA *= 3600. * 1000.
        deltaDec *= 3600. * 1000.
        # Much of the time we're closer than 1mas, but there are a few which hit higher values.
        print('max JPL errors', np.max(deltaRA), np.max(deltaDec))
        print('std JPL errors', np.std(deltaRA), np.std(deltaDec))
        self.assertLess(np.max(deltaRA), 25)
        self.assertLess(np.max(deltaDec), 10)
        self.assertLess(np.std(deltaRA), 2)
        self.assertLess(np.std(deltaDec), 1)


if __name__ == '__main__':
    unittest.main()
