import math
from unittest.result import failfast
import plotly.express as px 
import numpy as np  
import pandas as pd  
import plotly.graph_objects as plot
import plotly.express as px

# constructing the Signals
class Functions:
    #number of signals added
    numberSignalsAdded=-1
    #lists of added features of the Signals
    addedFreqs=[]
    addedAmps=[]
    addedPhases=[]
    addedSignals=[]
    composedAmp=np.zeros(1500)
    y_reconstructedSignal=np.zeros(1500)
    options_list=['Generated Signal','Composed Signal','recovered_time domain','recovered_freq domain']
    commonXaxis=np.linspace(0,2,1500).tolist()
    default_flag=1
    user_namedFile=''
tmax=2
n=1500
mainTimeAxis = np.linspace(0, tmax, n).tolist()  # Time Axis Array for all of the graphs

# default functions
def default_fun ():
    if (Functions.default_flag):
        add_signal(1, 0,1)
        Functions.default_flag=0

def layout_fig(fig):
    fig.update_layout(
        # autosize=False,
        width=700,
        height=400,
        xaxis_title="Time(s)",
        yaxis_title="Amplitude (mV)",
        margin=dict(
            l=50,
            r=50,
            b=50,
            t=50,
            pad=1
        ),
        
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        
    )
    return fig

# signal generater & mixer

def show_sin (magnitude, phase, frequency):  # Add new sin Signal
    Y_axis = np.zeros(1500)  # Array for saving sin Signals values
    for i in range(1500): 
        Y_axis[i] = (magnitude * (math.cos((2 * np.pi * frequency * mainTimeAxis[i]) + phase)))
    return px.line(x=mainTimeAxis, y=Y_axis)

def show_composed():  # Add new sin Signal
    return plot.Figure([plot.Scatter(x=mainTimeAxis, y=Functions.composedAmp)])

def add_signal(added_magnitude, added_phase,added_frequency):
    new_y_amplitude = np.zeros(1500)  # Array for saving sin Signals values
    for i in range(1500): 
        new_y_amplitude[i] = (added_magnitude * (math.cos((2 * np.pi * added_frequency * mainTimeAxis[i]) + added_phase))) 
    
    #updating lists
    Functions.numberSignalsAdded+=1
    Functions.addedFreqs.append(added_frequency)
    Functions.addedAmps.append(added_magnitude)
    Functions.addedPhases.append( added_phase)
    Functions.addedSignals.append(new_y_amplitude)
    Functions.composedAmp=np.add(Functions.composedAmp,new_y_amplitude)

    return plot.Figure([plot.Scatter(x=mainTimeAxis, y=Functions.composedAmp)])

def delete_signal(index_todelete): 

    if(Functions.numberSignalsAdded==0):
        clean_all()
        return plot.Figure([plot.Scatter(x=mainTimeAxis, y=Functions.composedAmp)])
    else:
        Functions.composedAmp=np.subtract(Functions.composedAmp,Functions.addedSignals[index_todelete] ) 
        Functions.addedAmps.pop(index_todelete)
        Functions.addedFreqs.pop(index_todelete)
        Functions.addedPhases.pop(index_todelete)
        Functions.addedSignals.pop(index_todelete)
        Functions.numberSignalsAdded-=1
        
        return plot.Figure([plot.Scatter(x=mainTimeAxis, y=Functions.composedAmp)])

def add_noise(addFlag, snr_db):
    signalSquared = Functions.composedAmp**2
    signal_avg=np.mean(signalSquared)
    signal_avg_db=10 * np.log10(signal_avg)
    noise_db=signal_avg_db - snr_db
    noise_actual=10 ** (noise_db/10)
    mean_noise=0
    noise=np.random.normal(mean_noise, np.sqrt(noise_actual),len(Functions.composedAmp))
    if(addFlag):
        Functions.composedAmp = Functions.composedAmp+noise
        fig=plot.Figure([plot.Scatter(x=mainTimeAxis, y=Functions.composedAmp)])
    else:
        noised_signal = Functions.composedAmp+noise
        fig =plot.Figure([plot.Scatter(x=mainTimeAxis, y=noised_signal)])
    return fig

def clean_all():
    #number of Signals added
    Functions.numberSignalsAdded=-1
    #lists of added features of the Signals
    Functions.addedFreqs=[]
    Functions.addedAmps=[]
    Functions.addedPhases=[]
    Functions.addedSignals=[]
    Functions.composedAmp=np.zeros(1500)
    Functions.composedAmp=np.zeros(1500)



# uploading and  downloading

def upload_signal(frequinces,amplitudes,phases,numberOfSignals):
    #updating lists
    signalsNumber=int(numberOfSignals[0])
    for signalIndex in range(0,signalsNumber):
        add_signal(amplitudes[signalIndex], phases[signalIndex],frequinces[signalIndex])
    return plot.Figure([plot.Scatter(x=mainTimeAxis, y=Functions.composedAmp)])

def save_signal():
    graph_axises = pd.DataFrame({'time':mainTimeAxis,'amp':Functions.composedAmp,'amp_reconstructed':Functions.y_reconstructedSignal})
    graph_detials = pd.DataFrame({ 
        'frequencies':Functions.addedFreqs,
        'amplitudes':Functions.addedAmps,
        'phases':Functions.addedPhases,
        'numberOfSignals':Functions.numberSignalsAdded+1
        
        })
    graph = pd.concat([graph_axises, graph_detials], axis=1) 
    # file_name=file_name+'.csv'   
    df = pd.DataFrame(graph) 
    # saving the dataframe 
    csv_file=df.to_csv()
    return csv_file

def save_signal_name(fileName):
    if (fileName==''):
        fileName='untitled'
    Functions.user_namedFile=fileName+'.csv'
# sampling , interpolation & converting to Freq domain 
def tofrqDomain_converter(yt):
    fs= n/tmax  
    fstep= fs/n
    f= np.linspace(0, (n-1)*fstep , n)
    yf_mag= np.abs(np.fft.fft(yt)) / n
    f_plot= f[0: int(n/2+1) ]
    y_f= 2 * yf_mag[0: int(n/2+1)]
    y_f[0]= y_f[0]/2   #dc component does't need to be multiplied by 2
    return f_plot , y_f

def sampling(samp_frq):
    samp_frq=samp_frq+1
    time_range=math.ceil(mainTimeAxis[-1]-mainTimeAxis[0])
    samp_rate=int((len(mainTimeAxis)/time_range)/samp_frq)
    samp_time=mainTimeAxis[::samp_rate]
    samp_amp= Functions.composedAmp[::samp_rate]
    return samp_time,samp_amp

def sinc_interp(samp_freq):
    samp_time,samp_amp=sampling(samp_freq)
    time_matrix= np.resize(mainTimeAxis,(len(samp_time),len(mainTimeAxis))) # to be able to sabstract nT from t
    
    k= (time_matrix.T - samp_time)/(samp_time[1]-samp_time[0]) 
    resulted_matrix = samp_amp* np.sinc(k)
    Functions.y_reconstructedSignal= np.sum(resulted_matrix, axis=1)
    reconstructed_fig = px.line(x=mainTimeAxis , y= Functions.y_reconstructedSignal)
    samplingPoints_fig = px.scatter(x=samp_time, y=samp_amp ,color_discrete_sequence=["red"],)
    x_f, y_f = tofrqDomain_converter(Functions.y_reconstructedSignal)
    return plot.Figure(data = reconstructed_fig.data + samplingPoints_fig.data), plot.Figure([plot.Scatter(x=x_f, y=y_f)])

