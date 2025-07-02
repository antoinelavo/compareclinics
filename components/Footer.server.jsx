import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400 p-[5em]">
      <div className="max-w-screen-xl mx-auto space-y-4">
        <div className="flex flex-col justify-between items-center md:flex-row md:justify-between gap-[4em] max-w-[70em] mx-auto">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Link href="/">
              
                <img
                  src="/images/mainlogo.png"
                  alt="Main Logo Logo"
                  className="h-10"
                />
              
            </Link>
          </div>

          {/* Links */}
          {/* <div className="flex flex-col md:flex-row flex-wrap items-start gap-4 font-medium text-gray-800 dark:text-gray-200">
            <Link href="/aboutus"><div className="hover:underline">소개</div></Link>
            <Link href="/blog"><div className="hover:underline">IB 관련 정보</div></Link>
            <Link href="/terms"><div className="hover:underline">이용약관</div></Link>
            <Link href="/privacy-policy"><div className="hover:underline">개인정보처리방침</div></Link>
            <Link href="/sat-hagwons"><div className="hover:underline">SAT 학원 추천</div></Link>
          </div> */}
        </div>
      </div>
      {/* <p className="text-center text-xs text-gray-300 mt-[10em]">IB Master | 사업자 등록 번호 634-10-03129 | 010 9785 3409 | 성남시 분당구 미금로 177 | 대표 박유진 </p> */}
    </footer>
  );
}