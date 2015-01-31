from dataframe import DataFrame
import array
from tempfile import TemporaryDirectory
from filecmp import cmp


def testArray():
    a=array.array('L')


def testWczytania():
    fieldnames=['IDStalej','WartoscStalej']
    fieldtypes=['L','f']
    df=DataFrame('bazadanych',fieldnames,fieldtypes)
    rec=df.Record(1,3.14)
    df.dodajByTuple(rec)
    df.dodajByTuple((2,2.79))    
    strtemp = TemporaryDirectory(dir='/tmp/temp')
    strPlik=strtemp.name + "/tmp.csv"
    df.zapisz(strPlik)
    df2=DataFrame.wczytaj(strPlik)
    df2.zapisz(strtemp.name + "/tmp2.csv")
    assert cmp(strPlik, strtemp.name + "/tmp2.csv",shallow=False)==True
    strtemp.cleanup()
    
def testManipulacji():
    fieldnames=['X','Y']
    fieldtypes=['L','f']
    df=DataFrame('XvsY',fieldnames, fieldtypes)
    rec=df.Record(0, 6.4)
    df.dodajByTuple(rec)
    df.dodajByTuple((1,3.5))
    df.dodajByTuple((2,2.1))
    df.dodajByTuple((3,1.97))
    x=df[0]
    assert x.tolist() == [0,1,2,3]
    
    y=df['X']
    assert y.tolist() == [0,1,2,3]
    y=df['Y']
    
    df.dodajByTuple((4,1.7))
    df.dodajByTuple((5,1.5))
    
    assert df.row(1) == {'X': 1, 'Y': 3.5}
    
    r=df.row(1)
    
    print(r['X']>2)
    print(r['X'])
    
    r=df.rows(lambda rec: rec['X']>2)
    ans=list()
    for row in r:
        print(row)
        ans.append(row['X'])
    
    assert ans == [3,4,5]
    
    
testManipulacji()