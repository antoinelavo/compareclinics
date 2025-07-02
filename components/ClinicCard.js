'use client';

import { useState } from 'react';

function getDeviceType() {
  if (typeof window === 'undefined') return 'unknown';
  const ua = navigator.userAgent;
  if (/mobile/i.test(ua)) return 'mobile';
  if (/tablet/i.test(ua)) return 'tablet';
  return 'desktop';
}


function extractLocation(address) {
  if (!address) return 'Seoul';
  
  // Extract district/area from address
  const districts = ['Gangnam-gu', 'Seocho-gu', 'Mapo-gu', 'Jung-gu', 'Yongsan-gu'];
  for (const district of districts) {
    if (address.includes(district)) {
      return district.replace('-gu', '');
    }
  }
  
  // Fallback to Seoul if no specific district found
  if (address.includes('Seoul')) return 'Seoul';
  return 'Korea';
}

export default function ClinicCard({ 
  name, 
  phone, 
  address, 
  services = [], 
  description, 
  url 
}) {
  const [showDetails, setShowDetails] = useState(false);
  const location = extractLocation(address);

  // Clean and format services
  const cleanServices = services.filter(service => 
    service && service.length > 0 && service.length < 50 && !service.includes('\n')
  );

  return (
    <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-200">
      <div className="flex flex-wrap justify-between flex-row items-start gap-y-[1em] sm:gap-y-[2em]">
        {/* Name and Location */}
        <div className="flex gap-[2em]">
          <div className="w-fill sm:w-[20em]">
            <a 
              href={url} 
              target="_blank" 
              rel="noopener noreferrer"
            >
              <h2 className="text-[1.1em] font-bold mb-2 text-[#111] m-0 hover:text-blue-600">
                {name}
              </h2>
            </a>
            <p className="text-sm text-gray-600 m-0">📍 {location}</p>
          </div>
        </div>

        {/* Truncated Description */}
        <div className="sm:flex-1 sm:mx-[2em] my-auto">
          {!showDetails && (
            <p className="text-sm text-gray-800 leading-relaxed line-clamp-2 my-auto">
              {description}
            </p>
          )}
        </div>

        {/* Show More Button */}
        <button 
          onClick={() => setShowDetails(prev => !prev)} 
          className="hidden sm:block my-auto hover:text-blue-600 transition-colors" 
        >
          {showDetails ? 
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-chevron-up">
              <path d="m18 15-6-6-6 6"/>
            </svg>
            :
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-chevron-down">
              <path d="m6 9 6 6 6-6"/>
            </svg>
          }
        </button>
      </div>

      {showDetails && (
        <div className="pt-4 text-gray-600 w-full mt-[1em]">
          {/* Services */}
          {cleanServices.length > 0 && (
            <div className="gap-2 w-full flex flex-wrap mb-4">
              {cleanServices.map((service, i) => (
                <span
                  key={i}
                  className="text-xs px-2 py-1.5 bg-[#e9f3ff] text-[#216eb3] rounded-full leading-none"
                >
                  {service.trim()}
                </span>
              ))}
            </div>
          )}
          
          {/* Description */}
          <p className="my-4 text-sm leading-[1.8em]">{description}</p>

          {/* Address */}
          <p className="mb-4 text-sm leading-[1.8em]">
            <span className="font-medium">주소:</span> {address}
          </p>

          {/* Phone */}
          {phone && (
            <p className="mb-4 text-sm leading-[1.8em]">
              <span className="font-medium">전화:</span> {phone}
            </p>
          )}

          {/* Contact Buttons */}
          <div className="flex gap-3 flex-wrap">
            {phone && (
              <a
                href={`tel:${phone}`}
                className="cursor-pointer px-4 py-2 text-sm bg-green-50 border border-green-300 rounded-lg text-green-800 flex items-center gap-2 hover:bg-green-100 hover:border-green-400 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                </svg>
                Call
              </a>
            )}
            
            <a 
              href={url}
              target="_blank" 
              rel="noopener noreferrer" 
              className="cursor-pointer px-4 py-2 text-sm bg-blue-50 border border-blue-300 rounded-lg text-blue-800 flex items-center gap-2 hover:bg-blue-100 hover:border-blue-400 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15,3 21,3 21,9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
              Visit Website
            </a>

          </div>
        </div>
      )}

      {/* Show More Button Mobile */}
      <button 
        onClick={() => setShowDetails(prev => !prev)} 
        className="block sm:hidden mt-[1em] mx-auto hover:text-blue-600 transition-colors" 
      >
        {showDetails ? 
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-chevron-up">
            <path d="m18 15-6-6-6 6"/>
          </svg>
          :
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-chevron-down">
            <path d="m6 9 6 6 6-6"/>
          </svg>
        }
      </button>
    </div>
  );
}

// Example usage with your data
function ClinicExample() {
  const sampleClinic = {
    "name": "JK PLASTIC",
    "phone": "+82-10-9738-4039",
    "address": "835, Nonhyeon-ro, Gangnam-gu, Seoul, Republic of Korea",
    "services": [
      "Rhinoplasty",
      "Breast"
    ],
    "description": "Korea's first and only plastic surgery clinic designated as a good medical institution to attract foreign patients by the Korean government. JK Plastic Surgery, located at the center of Medical Street in Apgujeong, Seoul, Korea.",
    "url": "https://www.jkplastic.com/en/"
  };

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <ClinicCard {...sampleClinic} />
    </div>
  );
}