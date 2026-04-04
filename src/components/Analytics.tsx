import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar
} from 'recharts';
import { BarChart3, TrendingUp, Users, Clock, Activity } from 'lucide-react';

const data = [
  { name: 'Jan', calls: 400, resolved: 240, escalated: 24 },
  { name: 'Feb', calls: 300, resolved: 139, escalated: 18 },
  { name: 'Mar', calls: 200, resolved: 980, escalated: 29 },
  { name: 'Apr', calls: 278, resolved: 390, escalated: 20 },
  { name: 'May', calls: 189, resolved: 480, escalated: 15 },
  { name: 'Jun', calls: 239, resolved: 380, escalated: 25 },
];

export default function Analytics() {
  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold text-secondary uppercase tracking-widest">Performance Insights</span>
          <h2 className="text-3xl font-extrabold text-on-surface font-headline mt-1">Advanced Analytics</h2>
          <p className="text-on-surface-variant mt-2 max-w-xl">Comprehensive data analysis of rural health interactions, outcomes, and operational efficiency.</p>
        </div>
        <div className="flex gap-2">
          <button className="bg-surface-container-low text-on-surface-variant px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider hover:bg-surface-container transition-colors">
            Last 30 Days
          </button>
          <button className="bg-secondary text-on-secondary px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider shadow-lg shadow-secondary/20">
            Export Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Avg. Call Duration', value: '4m 32s', trend: '+12%', icon: Clock, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Patient Satisfaction', value: '94.2%', trend: '+2.4%', icon: Users, color: 'text-teal-600', bg: 'bg-teal-50' },
          { label: 'AI Accuracy Rate', value: '98.1%', trend: '+0.5%', icon: Activity, color: 'text-purple-600', bg: 'bg-purple-50' },
          { label: 'Resolution Rate', value: '89.4%', trend: '-1.2%', icon: TrendingUp, color: 'text-amber-600', bg: 'bg-amber-50' },
        ].map((stat, i) => (
          <div key={i} className="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-surface-container">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-xl ${stat.bg} ${stat.color}`}>
                <stat.icon className="w-5 h-5" />
              </div>
              <span className={`text-[10px] font-black uppercase tracking-widest ${stat.trend.startsWith('+') ? 'text-teal-600' : 'text-red-600'}`}>
                {stat.trend}
              </span>
            </div>
            <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">{stat.label}</p>
            <h3 className="text-2xl font-black text-on-surface mt-1">{stat.value}</h3>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-surface-container">
          <h3 className="text-lg font-black text-on-surface mb-8 uppercase tracking-tight">Call Volume vs Resolution</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="colorCalls" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#006a71" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#006a71" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 10, fontWeight: 700, fill: '#64748b'}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fontSize: 10, fontWeight: 700, fill: '#64748b'}} />
                <Tooltip 
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', fontWeight: 700 }}
                />
                <Area type="monotone" dataKey="calls" stroke="#006a71" strokeWidth={3} fillOpacity={1} fill="url(#colorCalls)" />
                <Area type="monotone" dataKey="resolved" stroke="#3b82f6" strokeWidth={3} fillOpacity={0} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-surface-container">
          <h3 className="text-lg font-black text-on-surface mb-8 uppercase tracking-tight">Escalation Trends</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 10, fontWeight: 700, fill: '#64748b'}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fontSize: 10, fontWeight: 700, fill: '#64748b'}} />
                <Tooltip 
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', fontWeight: 700 }}
                />
                <Bar dataKey="escalated" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
