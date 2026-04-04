import React from 'react';
import { UserRound, Search, Filter, Star, MapPin, Phone, MessageSquare } from 'lucide-react';

const doctors = [
  {
    name: 'Dr. Rajesh Kumar',
    specialty: 'General Physician',
    location: 'Bihar Regional Center',
    rating: 4.8,
    availability: 'Available Now',
    image: 'https://picsum.photos/seed/doc1/200/200'
  },
  {
    name: 'Dr. Anjali Singh',
    specialty: 'Pediatrician',
    location: 'UP Health Hub',
    rating: 4.9,
    availability: 'In Call',
    image: 'https://picsum.photos/seed/doc2/200/200'
  },
  {
    name: 'Dr. Vikram Mehta',
    specialty: 'Cardiologist',
    location: 'MP Mobile Unit',
    rating: 4.7,
    availability: 'Available in 15m',
    image: 'https://picsum.photos/seed/doc3/200/200'
  },
  {
    name: 'Dr. Sunita Reddy',
    specialty: 'Dermatologist',
    location: 'Telangana Hub',
    rating: 4.6,
    availability: 'Available Now',
    image: 'https://picsum.photos/seed/doc4/200/200'
  }
];

export default function Doctors() {
  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold text-primary uppercase tracking-widest">Medical Network</span>
          <h2 className="text-3xl font-extrabold text-on-surface font-headline mt-1">Doctors Directory</h2>
          <p className="text-on-surface-variant mt-2 max-w-xl">Connect with specialized medical professionals for rural health escalations and consultations.</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant" />
            <input 
              type="text" 
              placeholder="Search doctors..." 
              className="pl-10 pr-4 py-2.5 bg-surface-container-low border-none rounded-xl text-sm font-bold focus:ring-primary-container outline-none w-64"
            />
          </div>
          <button className="p-2.5 bg-surface-container-low rounded-xl text-on-surface-variant hover:bg-surface-container transition-colors">
            <Filter className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {doctors.map((doc, i) => (
          <div key={i} className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-surface-container hover:shadow-md transition-all group">
            <div className="flex items-start gap-4">
              <img 
                src={doc.image} 
                alt={doc.name} 
                className="w-16 h-16 rounded-xl object-cover grayscale group-hover:grayscale-0 transition-all"
                referrerPolicy="no-referrer"
              />
              <div className="flex-1">
                <h3 className="font-bold text-on-surface text-lg leading-tight">{doc.name}</h3>
                <p className="text-primary text-xs font-bold uppercase tracking-wider mt-1">{doc.specialty}</p>
                <div className="flex items-center gap-1 mt-2 text-amber-500">
                  <Star className="w-3 h-3 fill-current" />
                  <span className="text-xs font-bold">{doc.rating}</span>
                </div>
              </div>
            </div>
            
            <div className="mt-6 space-y-3">
              <div className="flex items-center gap-2 text-on-surface-variant">
                <MapPin className="w-4 h-4" />
                <span className="text-xs font-medium">{doc.location}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${doc.availability === 'Available Now' ? 'bg-teal-500' : 'bg-amber-500'}`} />
                <span className="text-xs font-bold text-on-surface">{doc.availability}</span>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-surface-container flex gap-2">
              <button className="flex-1 bg-primary text-on-primary py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest hover:scale-[1.02] active:scale-95 transition-all">
                Schedule
              </button>
              <button className="p-2.5 bg-surface-container-low text-on-surface-variant rounded-xl hover:bg-surface-container transition-colors">
                <MessageSquare className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
