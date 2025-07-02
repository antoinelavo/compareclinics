import Link from 'next/link';
import ClinicCard from '@/components/ClinicCard';
import allClinicsData from '@/data/all_clinics.json';
import FilterLogic from './clinics/FilterLogic.client';

export const revalidate = 3600; // rebuild every hour


export default async function HagwonsPage({ searchParams }) {
  const sp = await searchParams;
  const selected = {
    region: Array.isArray(sp.region) ? sp.region : sp.region ? [sp.region] : [],
    lessonType: Array.isArray(sp.lessonType)
      ? sp.lessonType
      : sp.lessonType
      ? [sp.lessonType]
      : [],

    format: Array.isArray(sp.format) ? sp.format : sp.format ? [sp.format] : [],
    service: Array.isArray(sp.service) ? sp.service : sp.service ? [sp.service] : [],
  };
  console.log(selected)
  
  return (
    <main className="min-h-screen max-w-4xl mx-[5dvw] lg:mx-auto mb-[10em]">
      <h1>Compare Top Plastic Surgery Clinics in Korea</h1>

      <article>
        <p><strong>Updated:</strong> 2025-07-02</p>
        <p>At Compare Clinics, we simplify your search for plastic surgery in Korea by aggregating comprehensive clinic profiles, board-certified surgeons, genuine patient reviews, transparent pricing data, and before-and-after galleries—all in one user-friendly platform. Whether you’re considering rhinoplasty in Seoul, breast augmentation in Busan, or facelifts in Daegu, our side-by-side comparison tools and expert insights empower you to evaluate top-rated clinics across Korea at a glance. We update our listings regularly with the latest accreditation statuses, price packages, and special promotions, so you always have accurate, up-to-date information to make a confident, informed decision. Start your journey to aesthetic transformation today and discover why Korea remains the world’s premier destination for plastic surgery.</p>
      </article>

      {/* <FilterLinks selected={selected} /> */}

      <div className="space-y-5 flex flex-col mt-6" id="hagwon-list">
        {allClinicsData.map((card, i) => (
          <div
            key={`${card.id ?? 'hagwon'}-${i}`}
            data-hagwon
            data-region={card.region}
            data-lessontype={card.lessonType}
            data-format={card.format}
            data-service={card.ia_ee_tok ? 'IA,EE,TOK' : ''}
          >
            <ClinicCard {...card} priority={i === 0} />
          </div>
        ))}
      </div>

      {/* Hydrate client-side filtering logic */}
      <FilterLogic />
    </main>
  );
}

function FilterLinks({ selected }) {
  const base = '/';
  const filterGroups = [
    { title: 'Location', param: 'region', options: ['All', 'Seoul', 'Busan'] },
    { title: '추가 과목', param: 'service', options: ['IA', 'EE', 'TOK'] },
  ];

  return (
    <section className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm flex flex-wrap gap-x-[4em] gap-y-[3em] justify-center md:justify-start my-[1em]">
      {filterGroups.map(({ title, param, options }) => {
        const allOpts = options.filter(opt => opt !== '전체');
        const values = selected[param] || [];
        const isAllSelected = values.length === 0 || values.length === allOpts.length;
        return (
          <div key={param}>
            <h3 className="font-bold text-sm text-gray-800 mb-[1em] md:mb-[0.5em]">{title}</h3>
            <div className="flex flex-col md:flex-row gap-y-[0.75em] md:gap-x-[0.25em] min-w-[5em]">
              {options.map(option => {
                // Determine selection state and next params
                let updatedValues = [];

                if (option === '전체') {
                  // 전체 selects all or clears
                  updatedValues = isAllSelected ? [] : allOpts;
                } else {
                  // toggle this option
                  updatedValues = values.includes(option)
                    ? values.filter(v => v !== option)
                    : [...values, option];
                }

                // Build new query params
                const params = new URLSearchParams();
                Object.entries(selected).forEach(([key, vals]) => {
                  if (key === param) return;
                  vals.forEach(v => params.append(key, v));
                });
                updatedValues.forEach(v => params.append(param, v));
                const href = `${base}?${params.toString()}`;

                // Determine active styling
                const isActive =
                  option === '전체' ? isAllSelected : values.includes(option);

                return (
                  <Link
                    key={`${param}-${option}`}
                    href={href}
                    className={`text-sm px-3 py-1.5 rounded-full border transition font-medium shadow-sm whitespace-nowrap flex items-center gap-1 ${
                      isActive
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'text-gray-600 border-gray-300 hover:bg-gray-100 hover:border-gray-400'
                    }`}
                    scroll={false}
                  >
                    {isActive ? (
                      // Active
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="4"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="lucide lucide-check-icon mr-[0.25em]"
                      >
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    ) : (
                      // Inactive
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-circle-icon lucide-circle mr-[0.25em]"><circle cx="12" cy="12" r="10"/></svg>
                    )}
                    {option}
                  </Link>

                );
              })}
            </div>
          </div>
        );
      })}
    </section>
  );
}