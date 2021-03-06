#!/usr/bin/env python3

import sqlite3
import pandas as pd
import numpy as np

def get_motor_database():
    """
    Read the whole DC database and return all motors as a Pandas data table.
    """
    conn = sqlite3.connect("DCbase.dcd")
    motor_table = pd.read_sql_query("SELECT * from Motors", conn)
    conn.close()
    return motor_table

def get_prop_database():
    """
    Read the whole DC database and return all propellers as a Pandas data table.
    """
    conn = sqlite3.connect("DCbase.dcd")
    prop_table = pd.read_sql_query("SELECT * from Props", conn)
    conn.close()
    return prop_table

class PropellerStatic():
    """
    This class describes propellers at static conditions (zero airspeed).
    """
    
    def __init__(self):
        """
        Generate a generic prop without useful data.
        """
        self.Name = 'generic'
        print(self.Name)
        self.D = 10.0
        self.H = 5.0
        self.n10N = 8000.0
        self.n100W = 7000.0
        self.b = 2.0
        self.a = 10.0 / pow(self.n10N,self.b)
        self.d = 3.0
        self.c = 100.0 / pow(self.n100W,self.d)
        
    @classmethod
    def fromTable(cls, table, index):
        """
        Select one prop by index from the database table.
        """
        new = cls()
        my_prop = table[table['myid'] == index]
        new.Name = my_prop['Name'].item()
        print(new.Name)
        new.D = float(my_prop['Dia'])
        new.H = float(my_prop['Pitch'])
        new.b = float(my_prop['b'])
        new.d = float(my_prop['d'])
        new.n10N = float(my_prop['n10N'])
        new.n100W = float(my_prop['n100W'])
        # it is not clear what values of a and c are in the database
        # we compute it from n10N and n100W instead
        new.a = 10.0 / pow(new.n10N,new.b)
        new.c = 100.0 / pow(new.n100W,new.d)
        return new
    
    def ShaftPower(self, rpm):
        """
        Compute the power [W] needed to spin the propeller with the requested
        revolutions per minute.
        """
        P = self.c * pow(rpm,self.d)
        return(P)

    def Thrust(self, rpm):
        """
        Compute the Thrust [N] generated by the propeller spinning with the requested
        revolutions per minute.
        """
        T = self.a * pow(rpm,self.b)
        return(T)
    
    def fitPower(self, rpmList, pList):
        logP = np.log(np.array(pList))
        logN = np.log(np.array(rpmList))
        MatXT = np.matrix([np.ones_like(logN),logN])
        MatX = MatXT.transpose(1,0)
        MatXTXI = np.dot(MatXT,MatX).getI()
        MatXTY = np.dot(MatXT,logP)[0]
        corr = MatXTXI*MatXTY.transpose(1,0)
        self.c = np.exp(corr[0,0])
        self.d = corr[1,0]
        print('c=%g  d=%g' % (self.c, self.d))
        self.n100W = np.power(100.0/self.c, 1.0/self.d)
        print('n100W=%f' % self.n100W)

    def fitThrust(self, rpmList, tList):
        logT = np.log(np.array(tList))
        logN = np.log(np.array(rpmList))
        MatXT = np.matrix([np.ones_like(logN),logN])
        MatX = MatXT.transpose(1,0)
        MatXTXI = np.dot(MatXT,MatX).getI()
        MatXTY = np.dot(MatXT,logT)[0]
        corr = MatXTXI*MatXTY.transpose(1,0)
        self.a = np.exp(corr[0,0])
        self.b = corr[1,0]
        print('a=%g  b=%g' % (self.a, self.b))
        self.n10N = np.power(10.0/self.a, 1.0/self.b)
        print('n10N=%f' % self.n10N)
