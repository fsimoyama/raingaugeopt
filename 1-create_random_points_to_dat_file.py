import pandas as pd
import random
from shapely.geometry import Point,MultiPoint
import geopandas as gpd
from pyproj import CRS
import os
import time,datetime
import multiprocessing
import matplotlib.pyplot as plt

################################# Inputs #####################################
file = r'' #input file
outpath = ''
raio_metros = 1000
distrib = 'uniforme'
#uniforme #normal #log-normal

n_perturbacoes = 10000 #number of perturbations
clients = 29 #number of demand points
equipments = 7 #number of equipment
coverdist = 2000 #equipment covering distance
desvpad = 500 #std deviation - in case of normal distribution
##############################################################################
epsg_in = 31983
epsg = 31983

if outpath == '':
    outpath = os.path.join(os.path.dirname(file),'teste')
if os.path.exists(outpath)==False:
    os.mkdir(outpath)

df = pd.read_excel(file)
pontos = list(map(Point,df['Long'],df["Lat"]))
gdf = gpd.GeoDataFrame(df,geometry=pontos)
gdf.crs = CRS.from_epsg(epsg_in)
gdf.to_crs(epsg=epsg,inplace=True)

def create_dat_file(path,df,df2,n):
    with open(os.path.join(path,"MaxCoverageReal"+str(n)+".dat"),mode='w') as f:
        f.write('\n')
        f.write('\n')
        f.write(f'param clients := {clients};\n')
        f.write(f'param equipments := {equipments};\n')
        f.write(f'param coverdist := {coverdist};\n')
        f.write('\n')
        f.write('param weights := \n')
        for i in df.index:
            if i == df.index[-1]:
                f.write(f'{df["ID"][i]}\t{df["Weight"][i]};\n')
            else:
                f.write(f'{df["ID"][i]}\t{df["Weight"][i]}\n')
        f.write('\n')
        f.write('param populations := \n')
        for i in df.index:
            if i==df.index[-1]:
                f.write(f'{df["ID"][i]}\t{df["Population"][i]};\n')
            else:
                f.write(f'{df["ID"][i]}\t{df["Population"][i]}\n')
        f.write('\n')
        f.write('param a:\n')
        st=''
        for i in df['ID']:
            if i==df['ID'][df.index[-1]]:
                st+=f'\t{i}:=\n'
            else:
                st+=f'\t{i}'
        f.write(st)
        for i in df2.index:
            st = f'{i}\t'
            for m in df2.keys():
                if m == df2.keys()[-1]:
                    st += f'{df2[m][i]}\n'
                else:
                    st += f'{df2[m][i]}\t'
            if i == df2.index[-1]:
                st = st.replace('\n',';')
            f.write(st)

def gen_pontos(gdf,raio_metros):
    pontos_novos=[]
    for i in gdf.index:
        geo = gdf['geometry'][i].buffer(raio_metros)
        minx, miny, maxx, maxy = geo.bounds
        while True:
            if distrib == "uniforme":
                x = random.uniform(minx,maxx)
                y = random.uniform(miny,maxy)
            elif distrib == "normal":
                x,y = gdf['geometry'][i].xy
                x = x[0]
                y = y[0]
                x = random.gauss(x,desvpad)
                y = random.gauss(y,desvpad)
            elif distrib == "log-normal":
                x,y = gdf['geometry'][i].xy
                x = x[0]
                y = y[0]
                x = random.lognormvariate(x,desvpad)
                y = random.lognormvariate(y,desvpad)
                
            else:
                raise NameError(f"A distribuição {distrib} não existe")
            p  = Point(x,y)
            if distrib =="uniforme":
                if p.intersects(geo):
                    pontos_novos.append(p)
                    break
            else:
                pontos_novos.append(p)
                break
    return pontos_novos

media = 0

distancia_media = []
gdf3 = gdf.copy()
gdf3.set_index("ID",drop=True,inplace=True)
dic={}

shp_out=os.path.join(outpath,"shapes")

if os.path.exists(shp_out)==False:
    os.mkdir(shp_out)

for n in range(1,n_perturbacoes+1):
    t1 = time.time()
    pontos_novos = gen_pontos(gdf,raio_metros)
    gdf2 = gdf.copy()
    gdf2['geometry']=pontos_novos
    gdf2.set_index("ID",inplace=True)
    df2 = pd.DataFrame(index = df['ID'])

    dist_media = []
    for i in df2.index:
        geo = gdf2['geometry'][i]
        d = gdf2.distance(geo).to_list()
        add_to_list = False
        for m in d:
            if m == 0:
                add_to_list = True
            elif add_to_list:
                dist_media.append(m)
    
        df2[str(i)]=d

    df2[df2<=coverdist] = 1
    df2[df2>coverdist] = 0

    distancia_media.append(sum(dist_media)/len(dist_media))
    
    for i in df2.keys():
        df2[i] = pd.to_numeric(df2[i], downcast='integer')

    for i in gdf3.index:
        dist = gdf3['geometry'][i].distance(gdf2['geometry'][i])
        if i not in dic.keys():
            dic[i] = [dist]
        else:
            dic[i].append(dist)

    gdf2.to_file(os.path.join(shp_out,"MaxCoverageReal"+str(n)+".shp"))
    create_dat_file(outpath,df,df2,n)
    t2 = time.time()
    media+=(t2-t1)
    ts = time.time()+((media/n)*(n_perturbacoes-n))
    print(f'{n} de {n_perturbacoes}, previsão de termino: {datetime.datetime.fromtimestamp(ts)}')

df = pd.DataFrame({
            'ID': [i for i in range(1,n_perturbacoes+1)],
            "Dist_media": distancia_media
    })

df.set_index("ID",drop=True,inplace=True)
df.to_excel(os.path.join(outpath,'distancias.xlsx'))

##for i in dic.keys():
##    plt.hist(dic[i],bins=50)
##    plt.title(f"Estação {i}")
##    plt.show()
##    b = input("Break? : ")
##    if b=='s' or b=="S":
##        break




    
