
import matplotlib as mpl


# delete files if they exist
def purge_file(filenames):
    for filename in filenames:
        try:
                os.remove(filename)
        except OSError:
                print filename+' is not exist'

purge_file(['gelitaa_mp.mpbas','gelitaa_mp.mpend','gelitaa_mp.mplst','gelitaa_mp.mpnam', \
        'gelitaa_mp.mppth','gelitaa_mp.mpsim','gelitaa_mp.sloc','gelitaa_mp.timeseries'])

model_name=modelname
mp_namea = model_name + 'a_mp'
mp_nameb = model_name + 'b_mp'
pcoord = np.array([[0.000, 0.125, 0.500],
                   [0.000, 0.375, 0.500],
                   [0.000, 0.625, 0.500],
                   [0.000, 0.875, 0.500],
                   [1.000, 0.125, 0.500],
                   [1.000, 0.375, 0.500],
                   [1.000, 0.625, 0.500],
                   [1.000, 0.875, 0.500],
                   [0.125, 0.000, 0.500],
                   [0.375, 0.000, 0.500],
                   [0.625, 0.000, 0.500],
                   [0.875, 0.000, 0.500],
                   [0.125, 1.000, 0.500],
                   [0.375, 1.000, 0.500],
                   [0.625, 1.000, 0.500],
                   [0.875, 1.000, 0.500]])
#nodew = gwf.disv.ncpl.array * 2 + welcells['nodenumber'][0]
#plocs = [nodew for i in range(pcoord.shape[0])]

#plocs=np.ones(16)+10   np array is not working
# ----------------below works------------
#nodew=50
#plocs=[50]*16   # list is fine
#nodew=1000
#plocs=[1000]*16   # list is fine
## create particle data
#plocs = [(0, 0, 0), (0, 0, 1), (0, 0, 2)]
#pa = flopy.modpath.ParticleData(plocs, structured=False,
#                                localx=pcoord[:, 0],
#                                localy=pcoord[:, 1],
#                                localz=pcoord[:, 2],
#                                drape=0)
# ----------------above works------------
plocs=[]
for i in np.arange(5)+1:
    for j in np.arange(5)+1:
        plocs.append((0,i*18,j*18))
# what is plocs?
# plocs  --  Particle locations (zero-based) that are either layer, row, column locations or nodes.
# Local x-location of the particle in the cell. If a single value is provided all particles will have the same localx position. If a list, tuple, or np.ndarray is provided a localx position must be provided for each partloc. If localx is None, a value of 0.5 (center of the cell) will be used (default is None).
pa = flopy.modpath.ParticleData(plocs, structured=True, drape=0, \
                                        localx=0.5, localy=0.5, localz=0.5)

# create backward particle group
fpth = mp_namea + '.sloc'
pga = flopy.modpath.ParticleGroup(particlegroupname='BACKWARD1', particledata=pa,
                                  filename=fpth)
facedata = flopy.modpath.FaceDataType(drape=0,
                                      verticaldivisions1=10, horizontaldivisions1=10,
                                      verticaldivisions2=10, horizontaldivisions2=10,
                                      verticaldivisions3=10, horizontaldivisions3=10,
                                      verticaldivisions4=10, horizontaldivisions4=10,
                                      rowdivisions5=0, columndivisons5=0,
                                      rowdivisions6=4, columndivisions6=4)
#pb = flopy.modpath.NodeParticleData(subdivisiondata=facedata, nodes=nodew)
pb = flopy.modpath.NodeParticleData(subdivisiondata=facedata, nodes=plocs)
# create forward particle group
#fpth = mp_nameb + '.sloc'
#pgb = flopy.modpath.ParticleGroupNodeTemplate(particlegroupname='BACKWARD2', 
#                                              particledata=pb,
#                                              filename=fpth)


# create modpath files
mp = flopy.modpath.Modpath7(modelname=mp_namea, flowmodel=ms,
                            exe_name='mp7', model_ws='.')
flopy.modpath.Modpath7Bas(mp, porosity=0.2)
flopy.modpath.Modpath7Sim(mp, simulationtype='combined',
                          trackingdirection='backward',
                          weaksinkoption='pass_through',
                          weaksourceoption='pass_through',
                          referencetime=0.,
                          stoptimeoption='extend',
                          timepointdata=[10, 10000.],
                          particlegroups=pga)
'''
# timepointdata ---------
#List or tuple with 2 items that is only used if simulationtype is timeseries or combined. 
#If the second item is a float then the timepoint data corresponds to time point option 1 and 
#the first entry is the number of time points (timepointcount) and 
#the second entry is the time point interval. If the second item is a list, tuple, 
#or np.ndarray then the timepoint data corresponds to time point option 
#2 and the number of time points entries (timepointcount) in the second item and 
#the second item is an list, tuple, or array of user-defined time points. 
#If Timepointdata is None, time point option 1 is specified and the total simulation time is split into 100 intervals (default is None).
# seems to me that combined does time series
# write modpath datasets
'''
mp.write_input()

# run modpath
mp.run_model()

model_ws='.'
fpth = os.path.join(model_ws, mp_namea + '.mppth')
p = flopy.utils.PathlineFile(fpth)
p0 = p.get_alldata()

fpth = os.path.join(model_ws, mp_namea + '.timeseries')
ts = flopy.utils.TimeseriesFile(fpth)
ts0 = ts.get_alldata()

# this two lines could never be shown properly. was it because this is an output for mf6?
#fname = os.path.join(model_ws, model_name + '.disv.grb')
#grd = flopy.utils.MfGrdFile(fname, verbose=False)

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1, aspect='equal')
# everything associated with sr can not work at the moment
modelmap = flopy.plot.ModelMap(model=ms,rotation=0)  #suggested by flopy3_MapExample.ipynb
linecollection = modelmap.plot_grid()  # this line is the plotting line
quadmesh = modelmap.plot_ibound()
#ax.set_xlim(0, Lx)
#ax.set_ylim(0, Ly)
# mm is very important to trace all the particles
mm = flopy.plot.ModelMap(sr=dis.sr, ax=ax)
cmap = mpl.colors.ListedColormap(['r','g',])
#v = mm.plot_cvfd(verts, iverts, edgecolor='gray', a=ibd, cmap=cmap)
colors = ['green', 'orange', 'red']
for k in range(nlay):
       mm.plot_timeseries(ts0, layer=k, marker='o', lw=0, color=colors[k]);
mm.plot_pathline(p0, layer='all', color='blue', lw=0.75)
fig.show()




