import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  GraduationCap,
  School,
  Search,
  Filter,
  MapPin,
  ExternalLink,
  CheckCircle2,
  Building2,
  ChevronRight,
  ShieldCheck,
  ArrowLeft,
  RefreshCw
} from 'lucide-react';
import { api } from '../../services/api';

interface SchoolItem {
  school_id: string;
  school_name: string;
  district: string;
  state: string;
  school_type?: string;
  address?: string;
  established_year?: number;
  description?: string;
  public_phone?: string;
  website?: string;
  facilities?: string[];
  facilities_json?: string;
}

export const EducationPortalPage: React.FC = () => {
  const [schools, setSchools] = useState<SchoolItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('ALL');
  const [selectedSchool, setSelectedSchool] = useState<SchoolItem | null>(null);
  const [stats, setStats] = useState({
    total_schools: 10,
    districts_covered: 5,
    portal_url: 'http://localhost:5174'
  });

  const districts = ['ALL', 'Bengaluru Urban', 'Mysuru', 'Belagavi', 'Dharwad', 'Vijayapura', 'Ballari'];

  const getFacilitiesList = (school: SchoolItem): string[] => {
    if (Array.isArray(school.facilities) && school.facilities.length > 0) {
      return school.facilities;
    }
    if (school.facilities_json) {
      try {
        const parsed = typeof school.facilities_json === 'string'
          ? JSON.parse(school.facilities_json)
          : school.facilities_json;
        if (Array.isArray(parsed)) {
          return parsed.length > 0 ? parsed : ['Science Lab', 'Library', 'Sports Ground'];
        }
        if (parsed && Array.isArray(parsed.campus_facilities)) {
          return parsed.campus_facilities;
        }
        if (parsed && typeof parsed === 'object') {
          return ['Hostel', 'Workshops', 'Sports Arena', 'Health Center'];
        }
      } catch {
        // fallback
      }
    }
    return ['Science Lab', 'Library', 'Smart Classrooms', 'Sports Ground'];
  };

  useEffect(() => {
    // Automatically redirect to the Education Service on Port 5174
    window.location.replace('http://localhost:5174/');
  }, []);

  useEffect(() => {
    loadSchools();
    loadStats();
  }, [selectedDistrict]);

  const loadStats = async () => {
    try {
      const res = await api.education.getStats();
      if (res) {
        setStats({
          total_schools: res.total_schools || 10,
          districts_covered: res.districts_covered || 5,
          portal_url: res.portal_url || 'http://localhost:5174'
        });
      }
    } catch (e) {
      // Graceful fallback
    }
  };

  const loadSchools = async () => {
    setLoading(true);
    try {
      const res = await api.education.getSchools({
        q: searchQuery || undefined,
        district: selectedDistrict !== 'ALL' ? selectedDistrict : undefined,
      });
      if (res && res.items) {
        setSchools(res.items);
      }
    } catch (err) {
      console.error('Error fetching schools:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadSchools();
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-20">
      {/* Top Breadcrumb & Microservice Banner */}
      <div className="bg-navy-900 text-white border-b border-navy-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Link to="/" className="text-slate-300 hover:text-white flex items-center gap-1 transition-colors">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Central Portal</span>
            </Link>
            <span className="text-slate-600">/</span>
            <span className="text-saffron-400 font-bold">Education Service (शिक्षा सेवा)</span>
          </div>

          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>Microservice Online (Port 8001 / 5174)</span>
            </span>
          </div>
        </div>
      </div>

      {/* Hero Header */}
      <div className="bg-gradient-to-br from-navy-950 via-navy-900 to-blue-950 text-white pt-10 pb-16 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px]" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-xs font-bold mb-4">
              <GraduationCap className="w-4 h-4 text-blue-400" />
              <span>Department of School & Higher Education • Government of Karnataka</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight mb-4 text-white">
              Unified School Directory & <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-saffron-400 via-amber-300 to-emerald-400">
                Academic Service Network
              </span>
            </h1>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed mb-8">
              Discover verified government model schools, public schools, academic affiliations, RTE seats, DigiLocker certificates, and student admission portals across Karnataka.
            </p>

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-3.5 border border-white/10">
                <span className="text-xs text-slate-300 block">Verified Schools</span>
                <span className="text-2xl font-black text-saffron-400">{stats.total_schools}+</span>
              </div>
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-3.5 border border-white/10">
                <span className="text-xs text-slate-300 block">Districts Covered</span>
                <span className="text-2xl font-black text-emerald-400">{stats.districts_covered}</span>
              </div>
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-3.5 border border-white/10">
                <span className="text-xs text-slate-300 block">DigiLocker Integration</span>
                <span className="text-2xl font-black text-blue-300">100%</span>
              </div>
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-3.5 border border-white/10">
                <span className="text-xs text-slate-300 block">Scholarship Schemes</span>
                <span className="text-2xl font-black text-amber-300">Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Direct Portal Launch Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-7 relative z-20">
        <div className="bg-gradient-to-r from-saffron-500 via-amber-500 to-emerald-600 rounded-2xl p-1 shadow-xl">
          <div className="bg-white rounded-[14px] p-4 sm:p-5 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center shrink-0 border border-blue-200">
                <Building2 className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-navy-950 text-base">Full School Management & Admissions Portal</h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">Live</span>
                </div>
                <p className="text-xs text-slate-600">
                  Access student attendance, marksheets, OCR document uploads, staff invitations, and parent admission tracking on port 5174.
                </p>
              </div>
            </div>

            <a
              href="http://localhost:5174"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full md:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-navy-900 hover:bg-navy-800 text-white font-bold text-xs shadow-md hover:shadow-lg transition-all transform hover:-translate-y-0.5 shrink-0"
            >
              <span>Launch School Portal</span>
              <ExternalLink className="w-4 h-4 text-saffron-400" />
            </a>
          </div>
        </div>
      </div>

      {/* Main Content: Search, Filter, and Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-10">
        {/* Search and District Filter Controls */}
        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm mb-8 flex flex-col md:flex-row gap-4 items-center justify-between">
          {/* Search Form */}
          <form onSubmit={handleSearch} className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by school name, keyword, or district..."
              className="w-full pl-10 pr-4 py-2 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-saffron-500 focus:border-transparent"
            />
          </form>

          {/* District Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0 scrollbar-none">
            <span className="text-xs font-bold text-slate-500 mr-1 flex items-center gap-1 shrink-0">
              <Filter className="w-3.5 h-3.5" /> District:
            </span>
            {districts.map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setSelectedDistrict(d)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                  selectedDistrict === d
                    ? 'bg-navy-900 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="py-20 text-center">
            <RefreshCw className="w-8 h-8 text-saffron-500 animate-spin mx-auto mb-3" />
            <p className="text-sm font-bold text-slate-600">Retrieving official school records from microservice...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && schools.length === 0 && (
          <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center max-w-lg mx-auto shadow-sm">
            <div className="w-16 h-16 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-4 border border-amber-200">
              <School className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-navy-950 mb-1">No Schools Found</h3>
            <p className="text-xs text-slate-500 mb-6">
              No educational institutions matched your search filters. Try changing your district filter or keyword.
            </p>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedDistrict('ALL');
              }}
              className="px-4 py-2 rounded-xl bg-navy-900 text-white text-xs font-bold hover:bg-navy-800"
            >
              Reset Filters
            </button>
          </div>
        )}

        {/* School Cards Grid */}
        {!loading && schools.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {schools.map((school) => {
              const facilities = getFacilitiesList(school);

              return (
                <div
                  key={school.school_id}
                  className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between hover:-translate-y-1 relative group"
                >
                  <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-blue-500 to-indigo-600 opacity-80" />

                  <div>
                    {/* Header: ID & Type */}
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded-lg bg-blue-50 text-blue-800 border border-blue-200">
                        {school.school_id}
                      </span>
                      <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                        <ShieldCheck className="w-3 h-3 text-emerald-600" />
                        <span>{school.school_type || 'Government'}</span>
                      </span>
                    </div>

                    {/* School Name */}
                    <h3 className="text-base font-black text-navy-950 group-hover:text-blue-600 transition-colors mb-1.5">
                      {school.school_name}
                    </h3>

                    {/* Location */}
                    <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium mb-3">
                      <MapPin className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                      <span>{school.district}, {school.state}</span>
                    </div>

                    {/* Address snippet */}
                    {school.address && (
                      <p className="text-xs text-slate-600 line-clamp-2 mb-4 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        {school.address}
                      </p>
                    )}

                    {/* Facilities Pills */}
                    <div className="space-y-1.5 mb-4">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                        Campus Facilities:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {facilities.slice(0, 4).map((f: string, idx: number) => (
                          <span
                            key={idx}
                            className="inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200"
                          >
                            <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
                            <span>{f}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Card Footer: Action */}
                  <div className="mt-4 pt-3.5 border-t border-slate-100 flex items-center justify-between">
                    <button
                      onClick={() => setSelectedSchool(school)}
                      className="text-xs font-bold text-blue-600 hover:text-blue-800 inline-flex items-center gap-1"
                    >
                      <span>View Full Profile</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>

                    <a
                      href={`http://localhost:5174/#/schools/${school.school_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[11px] font-bold px-3 py-1.5 rounded-xl bg-navy-900 hover:bg-navy-800 text-white inline-flex items-center gap-1.5 transition-colors shadow-2xs"
                    >
                      <span>Admissions</span>
                      <ExternalLink className="w-3 h-3 text-saffron-400" />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* School Detail Modal */}
      {selectedSchool && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-xs">
          <div className="bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95 duration-200 relative">
            <button
              onClick={() => setSelectedSchool(null)}
              className="absolute top-4 right-4 w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center font-bold text-sm"
            >
              ✕
            </button>

            <div className="flex items-center gap-2 mb-2">
              <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                {selectedSchool.school_id}
              </span>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                {selectedSchool.school_type || 'State Board'}
              </span>
            </div>

            <h2 className="text-xl font-black text-navy-950 mb-2">
              {selectedSchool.school_name}
            </h2>

            <div className="flex items-center gap-1 text-xs text-slate-500 mb-4">
              <MapPin className="w-3.5 h-3.5 text-rose-500" />
              <span>{selectedSchool.district}, {selectedSchool.state}</span>
            </div>

            {selectedSchool.description && (
              <p className="text-xs text-slate-600 mb-4 leading-relaxed bg-slate-50 p-3 rounded-2xl border border-slate-200">
                {selectedSchool.description}
              </p>
            )}

            <div className="space-y-3 mb-6 text-xs text-slate-700">
              {selectedSchool.address && (
                <div className="flex items-start gap-2">
                  <span className="font-bold text-slate-400 shrink-0 w-24">Address:</span>
                  <span>{selectedSchool.address}</span>
                </div>
              )}
              {selectedSchool.established_year && (
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-400 shrink-0 w-24">Established:</span>
                  <span>{selectedSchool.established_year}</span>
                </div>
              )}
              {selectedSchool.public_phone && (
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-400 shrink-0 w-24">Phone:</span>
                  <a href={`tel:${selectedSchool.public_phone}`} className="text-blue-600 font-bold hover:underline">
                    {selectedSchool.public_phone}
                  </a>
                </div>
              )}
              {selectedSchool.website && (
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-400 shrink-0 w-24">Official Web:</span>
                  <a href={selectedSchool.website} target="_blank" rel="noreferrer" className="text-blue-600 font-bold hover:underline">
                    {selectedSchool.website}
                  </a>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                onClick={() => setSelectedSchool(null)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
              >
                Close
              </button>
              <a
                href={`http://localhost:5174/#/schools/${selectedSchool.school_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2 rounded-xl text-xs font-bold bg-navy-900 text-white hover:bg-navy-800 inline-flex items-center gap-1.5 shadow-md"
              >
                <span>Open in School Portal</span>
                <ExternalLink className="w-3.5 h-3.5 text-saffron-400" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
