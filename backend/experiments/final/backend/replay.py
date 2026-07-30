"""
replay_cmd.py - Reproduce un flujo tipo cmd del server a partir de un .txt de EEG ya grabado.
NO es la salida original (las ventanas caen en instantes distintos), pero re-genera
un flujo equivalente con el mismo pipeline (processing.py) y el mismo formato de prints.

Uso:
    python replay_cmd.py "ruta/online_WC_20260729_164922.txt"
    python replay_cmd.py "ruta/online_WC_...txt" --step 0.15 --window 4 --save
"""
import sys, os, time, argparse
import numpy as np, pandas as pd
from scipy.signal import butter, iirnotch, tf2sos, sosfiltfilt
from sklearn.cross_decomposition import CCA
import warnings; warnings.filterwarnings("ignore")

FS=250; USED=[4,5,6,7]; FREQS=[8.57,10.0,12.0,15.0]; H=[1,2,3]
EMOJI={8.57:"🍽️ Eat",10.0:"❄️ Cold",12.0:"📞 SOS",15.0:"🚽 WC"}
LBL2F={"Eat":8.57,"Cold":10.0,"SOS":12.0,"WC":15.0}

def _bp(): nyq=FS/2; return butter(4,[7/nyq,min(70/nyq,.999)],btype='bandpass',output='sos')
def _nt():
    o=[]
    for k in (1,2,3):
        f=50*k
        if f<FS/2:
            b,a=iirnotch(f,Q=30,fs=FS); o.append(tf2sos(b,a))
    return o
_SB=_bp(); _SN=_nt()
def preprocess(e):
    x=sosfiltfilt(_SB,e,axis=1); x=sosfiltfilt(_SB,x,axis=1)
    for s in _SN: x=sosfiltfilt(s,x,axis=1)
    x=x[USED,:]; return x-x.mean(0,keepdims=True)
def _refs(f,n):
    t=np.arange(n)/FS; c=[]
    for h in H: c+=[np.sin(2*np.pi*f*h*t),np.cos(2*np.pi*f*h*t)]
    return np.array(c).T
def _rho(X,Y):
    Xn=(X-X.mean(0))/(X.std(0)+1e-8); Yn=(Y-Y.mean(0))/(Y.std(0)+1e-8)
    c=CCA(1); c.fit(Xn,Yn); a,b=c.transform(Xn,Yn)
    return float(np.clip(abs(np.corrcoef(a[:,0],b[:,0])[0,1]),0,1))
def classify(e4):
    n=e4.shape[1]; X=e4.T.astype(float)
    cc={f:_rho(X,_refs(f,n)) for f in FREQS}; bf=max(cc,key=cc.get); return bf,cc[bf],cc

def target_from_name(path):
    for lbl,f in LBL2F.items():
        if f"online_{lbl}_" in os.path.basename(path): return f
    raise SystemExit("No reconozco la celda en el nombre del fichero")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("fichero")
    ap.add_argument("--window",type=float,default=4.0,help="ventana en s (def 4)")
    ap.add_argument("--step",type=float,default=0.15,help="paso deslizante en s (def 0.15)")
    ap.add_argument("--save",action="store_true",help="guardar la salida en <fichero>_replay.log")
    a=ap.parse_args()

    df=pd.read_csv(a.fichero,skiprows=4,skipinitialspace=True); df.columns=df.columns.str.strip()
    eeg=df[[f"EXG Channel {i}" for i in range(8)]].values.T.astype(float)
    target=target_from_name(a.fichero); WIN=int(FS*a.window); STEP=int(FS*a.step)

    out=open(a.fichero.rsplit(".",1)[0]+"_replay.log","w",encoding="utf-8") if a.save else None
    def emit(s):
        print(s)
        if out: out.write(s+"\n")

    emit("="*70)
    emit(f"  REPLAY (reconstruccion offline) de {os.path.basename(a.fichero)}")
    emit(f"  Objetivo: {EMOJI[target]} ({target} Hz) | ventana {a.window}s | paso {a.step}s")
    emit("  NOTA: flujo equivalente, NO identico al original (ventanas en otros instantes)")
    emit("="*70)
    cc=ct=0
    for s in range(0, eeg.shape[1]-WIN+1, STEP):
        t0=time.time()
        best,bcorr,corrs=classify(preprocess(eeg[:,s:s+WIN]))
        el=time.time()-t0
        ok=abs(best-target)<0.5; cc+=ok; ct+=1
        for f in FREQS: emit(f"[CCA] {f}Hz: {corrs[f]:.4f}")
        st="✅ CORRECT" if ok else f"❌ INCORRECT (detected {best:.2f}Hz)"
        emit(f"[Result] {EMOJI[target]}: Corr={bcorr:.4f} — {st}")
        emit(f"[Time elapsed] {el:.4f} (s)")
        emit(f"[SUMMARY] Accuracy: {cc}/{ct} ({cc/ct*100:.1f}%)")
    emit(f"\n[Replay] Final: {cc}/{ct} ({cc/ct*100:.1f}%)")
    if out: out.close(); print(f"\n[Replay] Guardado en {a.fichero.rsplit('.',1)[0]}_replay.log")

if __name__=="__main__":
    main()