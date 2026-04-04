import React from 'react';
import {
  ChevronLeft,
  Download,
  Languages,
  User,
  CheckCircle2,
  Play,
  Sparkles,
  FileText,
  Mic,
  Search,
  Bell
} from 'lucide-react';
import { cn } from '@/src/lib/utils';

const CALL_DATA_MAP: Record<string, any> = {
  '#IM-2940': {
    name: 'Rajesh Kumar',
    patientId: 'P-29931',
    age: '54y',
    gender: 'Male',
    region: 'Dharchula, UK',
    phone: '+91 98765 43210',
    startTime: '10:42 AM',
    duration: '4m 12s',
    outcome: 'Resolved by AI',
    summary: 'Patient reports mild fever (101.2°F), headache, and body aches. AI detected no respiratory distress. Recommended Paracetamol and rest.',
    symptoms: ['Mild Fever (101.2F)', 'Headache', 'Body Aches'],
    medicines: [
      { name: 'Paracetamol 500mg', instruction: 'Twice daily, after food', tag: 'OTC', tagClass: 'bg-secondary-container text-on-secondary-container' }
    ],
    transcript: [
      { isAgent: true, text: "Namaste! Main Immihelp AI hoon. Aapki tabiyat kaisi hai?", time: "10:42:05" },
      { isAgent: false, text: "Mujhe kal se halka bukhar hai aur sar mein dard ho raha hai.", time: "10:42:31" }
    ]
  },
  '#IM-2939': {
    name: 'Sunita Patil',
    patientId: 'P-29932',
    age: '42y',
    gender: 'Female',
    region: 'Nagpur, MH',
    phone: '+91 87654 32109',
    startTime: '09:15 AM',
    duration: '7m 45s',
    outcome: 'Escalated to Doctor',
    summary: 'Persistent dry cough for 2 weeks with sharp chest pain upon deep inhalation. Fatigue present. AI flags for physician review.',
    symptoms: ['Dry Cough', 'Chest Pain', 'Fatigue'],
    medicines: [
      { name: 'Amoxicillin 250mg', instruction: 'Pending Doctor Review', tag: 'PRESCRIPTION', tagClass: 'bg-error-container text-on-error-container' }
    ],
    transcript: [
      { isAgent: true, text: "Namaste Sunita ji. Aapko kya pareshani ho rahi hai?", time: "09:15:10" },
      { isAgent: false, text: "Mujhe do hafte se khansi hai aur seene mein dard hota hai jab saans leti hoon.", time: "09:16:05" }
    ]
  },
  '#IM-2938': {
    name: 'Amit Singh',
    patientId: 'P-29933',
    age: '29y',
    gender: 'Male',
    region: 'Lucknow, UP',
    phone: '+91 76543 21098',
    startTime: '08:00 AM',
    duration: '3m 22s',
    outcome: 'Resolved by AI',
    summary: 'Watery eyes and frequent sneezing. Seasonal allergy triggers suspected. Recommended Cetirizine 10mg.',
    symptoms: ['Watery Eyes', 'Sneezing', 'Allergy'],
    medicines: [
      { name: 'Cetirizine 10mg', instruction: 'Once daily, at night', tag: 'OTC', tagClass: 'bg-secondary-container text-on-secondary-container' }
    ],
    transcript: [
      { isAgent: true, text: "Namaste Amit ji. Kaise hain aap?", time: "08:00:15" },
      { isAgent: false, text: "Ankhon se pani gir raha hai aur bahut chhinkein aa rahi hain.", time: "08:00:45" }
    ]
  }
};

export default function CallDetails({ callId, onBack }: { callId: string, onBack: () => void }) {
  const data = CALL_DATA_MAP[callId] || CALL_DATA_MAP['#IM-2940'];

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
                  <p className="font-bold text-on-surface font-headline">{data.name}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <InfoItem label="Patient ID" value={data.patientId} />
                <InfoItem label="Gender / Age" value={`${data.gender}, ${data.age}`} />
                <InfoItem label="Village / Region" value={data.region} />
                <InfoItem label="Phone" value={data.phone} />
              </div>
            </div>
          </section>

          <section className="bg-surface-container-low p-6 rounded-xl">
            <h3 className="font-headline font-bold text-on-surface mb-4">Session Metrics</h3>
            <div className="space-y-4">
              <MetricRow label="Start Time" value={data.startTime} />
              <MetricRow label="Duration" value={data.duration} />
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-on-surface-variant font-medium">Outcome</span>
                <span className="flex items-center gap-1.5 text-primary font-bold text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  {data.outcome}
                </span>
              </div>
            </div>
          </section>

          <section className="bg-primary text-white p-6 rounded-xl shadow-lg relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-10 group-hover:scale-110 transition-transform duration-500">
              <Sparkles className="w-32 h-32" />
            </div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-[10px] font-bold uppercase tracking-widest opacity-70">AI Session Summary</span>
              <span className="text-[10px] bg-white/20 px-2 py-1 rounded font-bold backdrop-blur-sm">v2.4 Engine</span>
            </div>
            <div className="space-y-4 relative z-10">
              <p className="text-sm font-medium leading-relaxed text-white opacity-100 italic">
                "{data.summary}"
              </p>
              <div className="flex gap-2 pt-2">
                <button className="flex-1 bg-white/20 hover:bg-white/30 text-white border border-white/40 py-2.5 rounded-xl text-xs font-bold transition-all shadow-sm flex items-center justify-center gap-2 backdrop-blur-sm">
                  <FileText className="w-4 h-4 text-white" /> Export Report
                </button>
                <button className="flex-1 bg-white/10 hover:bg-white/20 py-2.5 rounded-xl border border-white/20 text-xs font-bold transition-all backdrop-blur-sm flex items-center justify-center gap-2 text-white">
                  <Play className="w-4 h-4 fill-current text-white" /> Play Session
                </button>
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
                {data.symptoms.map((s: string) => (
                  <span key={s} className="bg-emerald-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider shadow-md">
                    {s}
                  </span>
                ))}
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
              {data.transcript.map((msg: any, idx: number) => (
                <ChatMessage
                  key={idx}
                  isAgent={msg.isAgent}
                  text={msg.text}
                  time={msg.time}
                />
              ))}
            </div>
          </section>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-surface-container">
              <h3 className="font-headline font-bold text-on-surface mb-4">Recommended Medicines</h3>
              <div className="space-y-3">
                {data.medicines.map((med: any) => (
                  <MedicineItem key={med.name} name={med.name} instruction={med.instruction} tag={med.tag} tagClass={med.tagClass} />
                ))}
              </div>
            </section>

            <section className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-surface-container flex flex-col">
              <h3 className="font-headline font-bold text-on-surface mb-4">Admin Notes</h3>
              <textarea
                className="flex-1 w-full bg-surface-container-low border-none rounded-lg p-3 text-sm focus:ring-2 focus:ring-primary-container min-h-[100px] outline-none transition-all"
                placeholder="Add internal observations..."
              ></textarea>
              <button className="mt-4 bg-primary text-white py-2.5 rounded-xl font-bold text-sm shadow-sm hover:opacity-90 transition-opacity uppercase tracking-wider">
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

interface ChatMessageProps {
  isAgent?: boolean;
  text: string;
  time: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ isAgent, text, time }) => (
  <div className={cn("flex gap-4 max-w-[85%]", isAgent ? "" : "ml-auto flex-row-reverse")}>
    <div className={cn(
      "w-8 h-8 shrink-0 rounded-full flex items-center justify-center",
      isAgent ? "bg-primary-container text-on-primary-container" : "bg-surface-container-highest text-on-surface-variant"
    )}>
      {isAgent ? <Sparkles className="w-4 h-4 fill-current" /> : <User className="w-4 h-4" />}
    </div>
    <div className={cn(
      "p-4 rounded-2xl",
      isAgent ? "bg-emerald-600 text-white rounded-tl-none shadow-md shadow-emerald-500/10" : "bg-primary text-white rounded-tr-none shadow-sm"
    )}>
      <p className="text-sm leading-relaxed font-medium text-white">{text}</p>
      <span className={cn("text-[10px] font-bold mt-1 block text-white/50")}>{time}</span>
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
