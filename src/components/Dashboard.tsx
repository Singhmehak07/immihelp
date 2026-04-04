import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  Phone, 
  Sparkles, 
  AlertCircle, 
  FileCheck, 
  Stethoscope,
  Download,
  Mic,
  CheckCircle2,
  AlertTriangle,
  ChevronRight
} from 'lucide-react';
import { motion } from 'motion/react';
import { cn } from '@/src/lib/utils';

const volumeData = [
  { name: 'Mon', value: 110 },
  { name: 'Tue', value: 142 },
  { name: 'Wed', value: 125 },
  { name: 'Thu', value: 185 },
  { name: 'Fri', value: 130 },
  { name: 'Sat', value: 115 },
  { name: 'Sun', value: 155 },
];

const resolutionData = [
  { name: 'AI Resolved', value: 1078, color: '#006a71' },
  { name: 'Doctor Escalated', value: 206, color: '#bcd6ff' },
];

const StatCard = ({ icon: Icon, label, value, trend, colorClass, iconBgClass }: any) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-surface-container-lowest p-6 rounded-xl shadow-sm hover:shadow-md transition-all border border-transparent"
  >
    <div className="flex justify-between items-start mb-4">
      <span className={`p-2 rounded-lg ${iconBgClass}`}>
        <Icon className={`w-5 h-5 ${colorClass}`} />
      </span>
      <span className={`text-xs font-bold ${colorClass}`}>{trend}</span>
    </div>
    <p className="text-on-surface-variant text-[10px] font-bold uppercase tracking-wider">{label}</p>
    <h3 className="text-3xl font-black text-on-surface mt-1">{value}</h3>
  </motion.div>
);

export default function Dashboard() {
  return (
    <div className="p-6 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-4xl font-extrabold text-on-surface tracking-tight leading-tight">Overview Dashboard</h2>
          <p className="text-on-surface-variant max-w-2xl mt-1">Real-time health monitoring and voice AI performance analytics across rural clinical networks.</p>
        </div>
        <button className="bg-primary text-on-primary px-6 py-2.5 rounded-full font-semibold text-sm hover:opacity-90 transition-opacity flex items-center gap-2 shadow-lg shadow-primary/20">
          <Download className="w-4 h-4" />
          Export Report
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard 
          icon={Phone} 
          label="Total Calls" 
          value="1,284" 
          trend="+12%" 
          colorClass="text-primary" 
          iconBgClass="bg-primary-container" 
        />
        <StatCard 
          icon={Sparkles} 
          label="Resolved by AI" 
          value="1,078" 
          trend="84%" 
          colorClass="text-secondary" 
          iconBgClass="bg-secondary-container" 
        />
        <StatCard 
          icon={AlertCircle} 
          label="Escalated" 
          value="206" 
          trend="16%" 
          colorClass="text-tertiary" 
          iconBgClass="bg-tertiary-container" 
        />
        <StatCard 
          icon={FileCheck} 
          label="OTC Recs" 
          value="796" 
          trend="62%" 
          colorClass="text-primary" 
          iconBgClass="bg-primary-container/40" 
        />
        <StatCard 
          icon={Stethoscope} 
          label="Non-OTC Recs" 
          value="488" 
          trend="38%" 
          colorClass="text-on-surface-variant" 
          iconBgClass="bg-surface-container-highest" 
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Call Volume Chart */}
        <div className="lg:col-span-2 bg-surface-container-lowest p-8 rounded-xl shadow-sm space-y-6 border border-transparent">
          <div className="flex justify-between items-center">
            <div>
              <h4 className="text-lg font-bold text-on-surface">Daily Call Volume</h4>
              <p className="text-xs text-on-surface-variant">Monitoring load across 42 rural hubs</p>
            </div>
            <select className="bg-surface-container-low border-none rounded-lg text-xs font-semibold py-1.5 px-3 outline-none focus:ring-2 focus:ring-primary-container">
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={volumeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f4f5" />
                <XAxis 
                  dataKey="name" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fontSize: 10, fontWeight: 700, fill: '#adb3b5' }} 
                  dy={10}
                />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#adb3b5' }} />
                <Tooltip 
                  cursor={{ fill: '#f1f4f5' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}
                />
                <Bar 
                  dataKey="value" 
                  fill="#96f1fa" 
                  radius={[6, 6, 0, 0]} 
                  barSize={40}
                >
                  {volumeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index === 3 ? '#006a71' : '#96f1fa'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Case Mix Chart */}
        <div className="bg-surface-container-lowest p-8 rounded-xl shadow-sm space-y-8 flex flex-col border border-transparent">
          <h4 className="text-lg font-bold text-on-surface">Case Resolution Mix</h4>
          <div className="flex-1 flex flex-col items-center justify-center relative">
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={resolutionData}
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={0}
                    dataKey="value"
                    startAngle={90}
                    endAngle={450}
                  >
                    {resolutionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
                <span className="text-3xl font-black block text-on-surface">84%</span>
                <span className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">AI Accuracy</span>
              </div>
            </div>

            <div className="mt-8 space-y-2 w-full">
              {resolutionData.map((item) => (
                <div key={item.name} className="flex justify-between items-center px-4 py-2 bg-surface-container-low rounded-lg">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></span>
                    <span className="text-sm font-medium">{item.name}</span>
                  </div>
                  <span className="text-sm font-bold">{item.value.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Live Feed */}
      <section className="bg-surface-container-lowest rounded-xl shadow-sm p-8 border border-transparent">
        <div className="flex justify-between items-center mb-6">
          <h4 className="text-xl font-bold text-on-surface">Live Transcription Feed</h4>
          <span className="flex items-center gap-2 px-3 py-1 bg-primary-container rounded-full text-xs font-bold text-on-primary-container">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            AI Live Sync
          </span>
        </div>

        <div className="space-y-4">
          <FeedRow 
            icon={Mic} 
            iconColor="text-primary"
            patient="#4829" 
            hub="Sundarban Clinic" 
            text="...experiencing high fever for 3 days with dry cough..." 
            status="AI Processing"
            statusClass="bg-secondary-container text-on-secondary-container"
          />
          <FeedRow 
            icon={CheckCircle2} 
            iconColor="text-secondary"
            patient="#3920" 
            hub="Assam Hills North" 
            text="Recommended: Paracetamol 500mg, Rest." 
            status="OTC Resolved"
            statusClass="bg-primary-container text-on-primary-container"
            active
          />
          <FeedRow 
            icon={AlertTriangle} 
            iconColor="text-error"
            patient="#5102" 
            hub="Thar Remote Center" 
            text="Urgent escalation: Severe abdominal pain suspected appendicitis." 
            status="Escalated"
            statusClass="bg-error-container text-on-error-container"
            textClass="text-error font-medium"
          />
        </div>
      </section>
    </div>
  );
}

const FeedRow = ({ icon: Icon, iconColor, patient, hub, text, status, statusClass, textClass, active }: any) => (
  <div className={cn(
    "grid grid-cols-12 items-center py-4 px-4 transition-all rounded-lg group",
    active ? "bg-surface-container-low" : "hover:bg-surface-container-low"
  )}>
    <div className="col-span-1">
      <Icon className={cn("w-5 h-5", iconColor)} />
    </div>
    <div className="col-span-3">
      <p className="text-sm font-bold text-on-surface">Patient {patient}</p>
      <p className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">Hub: {hub}</p>
    </div>
    <div className={cn("col-span-5 text-sm text-on-surface-variant truncate pr-4", textClass)}>
      "{text}"
    </div>
    <div className="col-span-2">
      <span className={cn("px-3 py-1 text-[10px] font-bold rounded-full uppercase tracking-wider", statusClass)}>
        {status}
      </span>
    </div>
    <div className="col-span-1 text-right">
      <button className={cn(
        "transition-opacity p-2 hover:bg-surface-container-lowest rounded-full",
        !active && "opacity-0 group-hover:opacity-100"
      )}>
        <ChevronRight className="w-4 h-4 text-primary" />
      </button>
    </div>
  </div>
);
