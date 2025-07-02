'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function FilterLogic() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const cards = Array.from(document.querySelectorAll('[data-hagwon]'));
    const region = searchParams.getAll('region');
    const lessonType = searchParams.getAll('lessonType');
    const format = searchParams.getAll('format');
    const service = searchParams.getAll('service');

    cards.forEach(card => {
      const cardRegion = card.dataset.region || '';
      const cardLessonType = card.dataset.lessontype?.split(',') || [];
      const cardFormat = card.dataset.format?.split(',') || [];
      const cardService = card.dataset.service?.split(',') || [];

      const matches =
        (region.length === 0 || region.some(r => cardRegion.includes(r))) &&
        (lessonType.length === 0 || lessonType.every(l => cardLessonType.includes(l))) &&
        (format.length === 0 || format.every(f => cardFormat.includes(f))) &&
        (service.length === 0 || service.every(s => cardService.includes(s)));

      card.style.display = matches ? 'block' : 'none';
    });
  }, [searchParams]);

  return null;
}