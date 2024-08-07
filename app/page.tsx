"use client";
import Link from 'next/link';

export default function Home() {
  return (
    <div className="container">
      <h1>Rainbow Six Siege Roulette</h1>
      <Link href="/roulette">Go to Roulette</Link>
      <style jsx>{`
        .container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100vh;
          text-align: center;
        }
        
      `}</style>
    </div>
  );
}