import Link from 'next/link';
import HagwonCard from '@/components/ClinicCard';
import allHagwonsData from '@/data/hagwons';
import FilterLogic from './FilterLogic.client';

export const revalidate = 3600; // rebuild every hour

export const metadata = {
  title: 'IB 학원 29곳 추천 및 비교 [2025년 최신]',
  description: 'IB 학원 추천, 비교, 선택 가이드 – 2025년 최신 업데이트',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/images/favicon.ico'
  },

  openGraph: {
    title: 'IB 학원 29곳 추천 및 비교 [2025년 최신]',
    description: 'IB 학원 추천, 비교, 선택 가이드 – 2025년 최신 업데이트',
    url: 'https://ibmaster.net/hagwons',
    siteName: 'IB Master',
    locale: 'ko-KR',
    type: 'website',
  },
}

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
      <h1>IB 학원 29곳 추천 및 비교 [2025년 최신]</h1>

      <article>
        <p><strong>최신 업데이트:</strong> 2025년 6월 16일</p>
        <p>IB 학원은 IB 과정을 이수 중이거나 준비 중인 학생들에게 집중적인 도움을 제공합니다. 본 페이지는 학부모와 학생들이 신뢰할 수 있는 IB 학원을 선택할 수 있도록 도움을 주는 것을 목적으로 하며, 학원 선택 시 고려해야 할 요소, 수업 구성, 과외와의 차이점 등을 상세히 안내합니다.</p>
      </article>

      <FilterLinks selected={selected} />

      <div className="space-y-5 flex flex-col mt-6" id="hagwon-list">
        {allHagwonsData.map((card, i) => (
          <div
            key={`${card.id ?? 'hagwon'}-${i}`}
            data-hagwon
            data-region={card.region}
            data-lessontype={card.lessonType}
            data-format={card.format}
            data-service={card.ia_ee_tok ? 'IA,EE,TOK' : ''}
          >
            <HagwonCard {...card} priority={i === 0} />
          </div>
        ))}
      </div>

      {/* Hydrate client-side filtering logic */}
      <FilterLogic />
    </main>
  );
}

function FilterLinks({ selected }) {
  const base = '/hagwons';
  const filterGroups = [
    { title: '지역', param: 'region', options: ['전체', '강남', '서초', '제주', '부산', '해외'] },
    { title: '수업 방식', param: 'lessonType', options: ['개인', '그룹'] },
    { title: '수업 형태', param: 'format', options: ['대면', '온라인'] },
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