import { 
  ChevronLeft, 
  Download, 
  Languages, 
  User, 
  CheckCircle2, 
  Play, 
  Stethoscope, 
  Sparkles, 
  FileText,
  Mic,
  Search,
  Bell
} from 'lucide-react';
import { cn } from '@/src/lib/utils';

export default function CallDetails({ callId, onBack }: { callId: string, onBack: () => void }) {
  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="p-2 hover:bg-surface-container rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="flex flex-col">
            <h2 className="text-xl font-bold tracking-tight text-primary font-headline">Call Details</h2>
            <span className="text-xs text-on-surface-variant font-bold uppercase tracking-wider">Log ID: {callId}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex bg-surface-container-low px-4 py-1.5 rounded-full items-center gap-2 group focus-within:ring-2 focus-within:ring-primary-container transition-all">
            <Search className="w-4 h-4 text-on-surface-variant group-focus-within:text-primary" />
            <input 
              type="text" 
              placeholder="Search patient ID..." 
              className="bg-transparent border-none focus:ring-0 text-sm w-48 outline-none"
            />
          </div>
          <button className="p-2 text-on-surface-variant hover:bg-surface-container rounded-full relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full"></span>
          </button>
        </div>
      </div>

      {/* Bento Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <section className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-surface-container">
            <div className="flex justify-between items-start mb-6">
              <h3 className="font-headline font-bold text-on-surface">Patient Identity</h3>
              <span className="bg-primary-container text-on-primary-container px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">Verified</span>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center text-primary">
                  <User className="w-7 h-7" />
                </div>
                <div>
                  <p className="text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">Name</p>
                  <p className="font-bold text-on-surface font-headline">Rajesh Mehra</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 pt-2">
                <InfoItem label="Patient ID" value="P-29931" />
                <InfoItem label="Gender / Age" value="Male, 54y" />
                <InfoItem label="Village / Region" value="Dharchula, UK" />
                <InfoItem label="Phone" value="+91 98XXX-X231" />
              </div>
            </div>
          </section>

          <section className="bg-surface-container-low p-6 rounded-xl">
            <h3 className="font-headline font-bold text-on-surface mb-4">Session Metrics</h3>
            <div className="space-y-4">
              <MetricRow label="Start Time" value="10:42 AM" />
              <MetricRow label="End Time" value="10:56 AM" />
              <MetricRow label="Duration" value="14m 22s" />
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-on-surface-variant font-medium">Outcome</span>
                <span className="flex items-center gap-1.5 text-primary font-bold text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  Prescription Issued
                </span>
              </div>
            </div>
          </section>

          <section className="bg-on-surface text-surface p-6 rounded-xl shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[10px] font-bold uppercase tracking-widest opacity-60">Call Recording</span>
              <span className="text-[10px] bg-surface/10 px-2 py-1 rounded font-bold">MP3 128kbps</span>
            </div>
            <div className="flex items-center gap-4">
              <button className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-on-primary hover:scale-105 transition-transform">
                <Play className="w-5 h-5 fill-current" />
              </button>
              <div className="flex-1">
                <div className="h-1 bg-surface/20 rounded-full overflow-hidden mb-2">
                  <div className="h-full bg-primary-container w-[35%] rounded-full"></div>
                </div>
                <div className="flex justify-between text-[10px] font-bold opacity-70">
                  <span>04:52</span>
                  <span>14:22</span>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* Right Column */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-surface-container">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-1.5 h-6 bg-primary rounded-full"></div>
                <h3 className="font-headline font-bold text-on-surface">Reported Symptoms</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {['Persistent Cough', 'Mild Fever (100.2F)', 'Shortness of Breath', 'Fatigue'].map(s => (
                  <span key={s} className="bg-secondary-container text-on-secondary-container px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider">
                    {s}
                  </span>
                ))}
              </div>
            </section>

            <section className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-surface-container border-l-4 border-tertiary">
              <div className="flex items-center gap-2 mb-4">
                <Stethoscope className="w-5 h-5 text-tertiary" />
                <h3 className="font-headline font-bold text-on-surface">Doctor Handoff</h3>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center">
                    <FileText className="w-5 h-5 text-on-surface-variant" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-on-surface">Dr. Anjali Sharma</p>
                    <p className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">Pending Review</p>
                  </div>
                </div>
                <button className="text-primary text-xs font-bold hover:underline uppercase tracking-wider">Escalate</button>
              </div>
            </section>
          </div>

          {/* Transcript */}
          <section className="bg-surface-container-lowest rounded-xl shadow-sm overflow-hidden flex flex-col h-[400px] border border-surface-container">
            <div className="p-5 bg-surface-container-low flex justify-between items-center border-b border-surface-container">
              <h3 className="font-headline font-bold text-on-surface">AI Voice Transcript</h3>
              <div className="flex gap-2">
                <button className="p-1.5 rounded-lg hover:bg-surface-container-high transition-colors text-on-surface-variant">
                  <Languages className="w-5 h-5" />
                </button>
                <button className="p-1.5 rounded-lg hover:bg-surface-container-high transition-colors text-on-surface-variant">
                  <Download className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar bg-[radial-gradient(#ebeef0_1px,transparent_1px)] [background-size:20px_20px]">
              <ChatMessage 
                isAgent 
                text="Namaste! Main Immihelp AI hoon. Aapki tabiyat kaisi hai? Kya aapko koi pareshani ho rahi hai?" 
                time="10:42:05" 
              />
              <ChatMessage 
                text="Mujhe do din se bukhar hai aur khansi bahut zyada aa rahi hai. Saans lene mein bhi thodi dikkat hai." 
                time="10:42:31" 
              />
              <ChatMessage 
                isAgent 
                text="Kshama chahta hoon sunkar. Kya aapne koi dawai li hai abhi tak? Aur kya khansi ke saath balgam aa raha hai?" 
                time="10:43:10" 
              />
            </div>
          </section>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-surface-container">
              <h3 className="font-headline font-bold text-on-surface mb-4">Recommended Medicines</h3>
              <div className="space-y-3">
                <MedicineItem name="Paracetamol 500mg" instruction="Twice daily, after food" tag="OTC" tagClass="bg-secondary-container text-on-secondary-container" />
                <MedicineItem name="Amoxicillin 250mg" instruction="Three times daily, 5 days" tag="PRESCRIPTION" tagClass="bg-error-container text-on-error-container" />
              </div>
            </section>
            
            <section className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-surface-container flex flex-col">
              <h3 className="font-headline font-bold text-on-surface mb-4">Admin Notes</h3>
              <textarea 
                className="flex-1 w-full bg-surface-container-low border-none rounded-lg p-3 text-sm focus:ring-2 focus:ring-primary-container min-h-[100px] outline-none transition-all" 
                placeholder="Add internal observations..."
              ></textarea>
              <button className="mt-4 bg-primary text-on-primary py-2.5 rounded-xl font-bold text-sm shadow-sm hover:opacity-90 transition-opacity uppercase tracking-wider">
                Save Session Changes
              </button>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

const InfoItem = ({ label, value }: { label: string, value: string }) => (
  <div>
    <p className="text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">{label}</p>
    <p className="text-sm font-semibold text-on-surface">{value}</p>
  </div>
);

const MetricRow = ({ label, value }: { label: string, value: string }) => (
  <div className="flex justify-between items-center py-2 border-b border-surface-container-high">
    <span className="text-sm text-on-surface-variant font-medium">{label}</span>
    <span className="text-sm font-bold text-on-surface">{value}</span>
  </div>
);

const ChatMessage = ({ isAgent, text, time }: { isAgent?: boolean, text: string, time: string }) => (
  <div className={cn("flex gap-4 max-w-[85%]", isAgent ? "" : "ml-auto flex-row-reverse")}>
    <div className={cn(
      "w-8 h-8 shrink-0 rounded-full flex items-center justify-center",
      isAgent ? "bg-primary-container text-on-primary-container" : "bg-surface-container-highest text-on-surface-variant"
    )}>
      {isAgent ? <Sparkles className="w-4 h-4 fill-current" /> : <User className="w-4 h-4" />}
    </div>
    <div className={cn(
      "p-4 rounded-2xl",
      isAgent ? "bg-surface-container rounded-tl-none text-on-surface" : "bg-primary text-on-primary rounded-tr-none"
    )}>
      <p className="text-sm leading-relaxed font-medium">{text}</p>
      <span className={cn("text-[10px] font-bold mt-1 block opacity-40", !isAgent && "opacity-60")}>{time}</span>
    </div>
  </div>
);

const MedicineItem = ({ name, instruction, tag, tagClass }: any) => (
  <div className="flex items-center justify-between p-3 bg-surface-container-low rounded-lg">
    <div>
      <p className="text-sm font-bold text-on-surface">{name}</p>
      <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">{instruction}</p>
    </div>
    <span className={cn("px-2 py-0.5 rounded text-[10px] font-black tracking-widest", tagClass)}>{tag}</span>
  </div>
);
