import { 
  Search, 
  Bell, 
  Mic, 
  Pill, 
  Filter, 
  ChevronRight,
  AlertCircle
} from 'lucide-react';
import { cn } from '@/src/lib/utils';

const escalations = [
  {
    id: '#CAL-9821',
    initials: 'RM',
    patient: 'Rajesh Mishra',
    urgent: true,
    symptoms: 'Severe chest pain, radiating to left arm, shortness of breath, perspiration.',
    reason: 'High Risk Cardiac',
    aiFlag: 'Non-OTC Severity',
    med: 'Aspirin 300mg',
    doctor: 'Dr. Kavita S.',
    status: 'Active Review',
    time: '2m ago'
  },
  {
    id: '#CAL-9818',
    initials: 'AS',
    patient: 'Anita Singh',
    urgent: false,
    symptoms: 'High fever (103°F) for 3 days, persistent vomiting, severe dehydration.',
    reason: 'Pediatric Escalation',
    aiFlag: 'Ref: Potential Dengue',
    med: 'IV Fluids / Paracetamol',
    doctor: null,
    status: 'Unassigned',
    time: '14m ago'
  },
  {
    id: '#CAL-9815',
    initials: 'BK',
    patient: 'Bimal Kumar',
    urgent: true,
    symptoms: 'Sudden vision loss in right eye, headache, dizziness, history of hypertension.',
    reason: 'Neurological Fluctuation',
    aiFlag: 'AI-Flag: Urgent Specialist',
    med: 'Immediate Observation',
    doctor: 'Dr. Rahul M.',
    status: 'In Consultation',
    time: '28m ago'
  }
];

export default function Escalations() {
  return (
    <div className="p-8 max-w-7xl mx-auto w-full space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-4xl font-extrabold text-on-surface font-headline tracking-tight mb-2">Escalation Queue</h2>
        <div className="flex items-center gap-2">
          <div className="bg-primary-container px-3 py-1 rounded-full flex items-center gap-2">
            <Mic className="w-3.5 h-3.5 text-on-primary-container" />
            <span className="text-[10px] font-black text-on-primary-container uppercase tracking-widest">8 Critical AI Referrals</span>
          </div>
          <span className="text-on-surface-variant text-sm font-medium">Monitoring rural health hub activity in real-time.</span>
        </div>
      </div>

      {/* Stats Bento */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="col-span-1 md:col-span-2 bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-surface-container flex flex-col justify-between">
          <div>
            <p className="text-[10px] font-black text-primary uppercase tracking-widest mb-1">Queue Health</p>
            <p className="text-3xl font-extrabold text-on-surface font-headline">94% Resolved</p>
          </div>
          <div className="mt-4 flex -space-x-2">
            {['SM', 'AK', 'PD'].map((initials, i) => (
              <div 
                key={i} 
                className="h-8 w-8 rounded-full bg-surface-container-high flex items-center justify-center ring-2 ring-surface-container-lowest text-[10px] font-black text-on-surface shadow-sm"
              >
                {initials}
              </div>
            ))}
            <div className="h-8 w-8 rounded-full bg-surface-container flex items-center justify-center ring-2 ring-surface-container-lowest text-[10px] font-black text-on-surface-variant">+4</div>
          </div>
        </div>
        
        <div className="bg-error-container/10 p-6 rounded-xl border border-error-container/20">
          <p className="text-[10px] font-black text-error uppercase tracking-widest mb-1">High Urgency</p>
          <p className="text-4xl font-extrabold text-error font-headline">03</p>
          <p className="text-[10px] font-bold text-on-error-container mt-2 uppercase tracking-wider">Requires immediate specialist intervention</p>
        </div>
        
        <div className="bg-secondary-container/10 p-6 rounded-xl border border-secondary-container/20">
          <p className="text-[10px] font-black text-secondary uppercase tracking-widest mb-1">Avg Response</p>
          <p className="text-4xl font-extrabold text-secondary font-headline">12m</p>
          <p className="text-[10px] font-bold text-on-secondary-container mt-2 uppercase tracking-wider">Voice AI to specialist handoff</p>
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface-container-low rounded-xl overflow-hidden border border-surface-container">
        <div className="px-6 py-4 bg-surface-container-lowest flex justify-between items-center border-b border-surface-container">
          <div className="flex gap-4">
            <button className="text-sm font-bold text-primary border-b-2 border-primary pb-1">Non-OTC Only</button>
            <button className="text-sm font-bold text-on-surface-variant hover:text-primary transition-colors">Specialist Review</button>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-surface-container text-on-surface-variant rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-surface-container-high transition-colors">
            <Filter className="w-3.5 h-3.5" />
            Advanced Filters
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="text-[10px] text-on-surface-variant font-black uppercase tracking-widest border-b border-surface-container">
                <th className="px-6 py-5">Patient & ID</th>
                <th className="px-6 py-5">Symptoms</th>
                <th className="px-6 py-5">Escalation Reason</th>
                <th className="px-6 py-5">Suggested Med</th>
                <th className="px-6 py-5 text-center">Status</th>
                <th className="px-6 py-5 text-right">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-container">
              {escalations.map((esc) => (
                <tr key={esc.id} className="group hover:bg-surface-container-lowest transition-colors">
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "h-10 w-10 rounded-full flex items-center justify-center font-black text-xs shadow-sm",
                        esc.urgent ? "bg-error-container/20 text-error" : "bg-surface-container-high text-on-surface"
                      )}>{esc.initials}</div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-on-surface text-sm">{esc.patient}</span>
                          {esc.urgent && <span className="bg-error text-on-error text-[10px] font-black px-1.5 py-0.5 rounded uppercase tracking-widest">Urgent</span>}
                        </div>
                        <div className="text-[10px] text-on-surface-variant font-bold tracking-widest">{esc.id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5 max-w-xs">
                    <p className="text-sm text-on-surface-variant line-clamp-2 font-medium leading-relaxed">{esc.symptoms}</p>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex flex-col gap-1">
                      <span className={cn(
                        "text-[10px] font-black w-fit px-2 py-0.5 rounded uppercase tracking-widest",
                        esc.urgent ? "text-error bg-error-container/10" : "text-primary-dim bg-primary-container/20"
                      )}>{esc.reason}</span>
                      <span className="text-[10px] text-on-surface-variant italic font-medium">{esc.aiFlag}</span>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-2">
                      <Pill className="w-3.5 h-3.5 text-secondary" />
                      <span className="text-sm font-bold text-on-surface">{esc.med}</span>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex flex-col items-center gap-1">
                      {esc.doctor ? (
                        <>
                          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-highest">
                            <div className={cn("w-1.5 h-1.5 rounded-full", esc.urgent ? "bg-error animate-pulse" : "bg-primary")}></div>
                            <span className="text-[10px] font-black text-on-surface uppercase tracking-widest">{esc.doctor.replace('Dr.', 'Spcl.')}</span>
                          </div>
                          <span className="text-[10px] text-on-surface-variant font-bold uppercase tracking-widest">{esc.status}</span>
                        </>
                      ) : (
                        <button className="px-4 py-1.5 bg-primary text-on-primary rounded-full text-[10px] font-black uppercase tracking-widest shadow-sm hover:scale-95 transition-transform">
                          Assign Specialist
                        </button>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-5 text-right">
                    <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest">{esc.time}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
