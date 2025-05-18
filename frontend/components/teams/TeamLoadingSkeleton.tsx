import React from 'react';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Loading skeleton for team detail view.
 *
 * Mimics the card layout of TeamDetail for loading state.
 *
 * Returns
 * -------
 * JSX.Element
 *     The rendered skeleton component.
 */
const TeamLoadingSkeleton: React.FC = () => (
  <div className="w-full max-w-4xl mx-auto p-4">
    <Skeleton className="h-10 w-1/2 mx-auto mb-8" />
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-card shadow-lg rounded-xl overflow-hidden">
        <div className="flex flex-col items-center justify-center p-6 h-[200px] space-y-3">
          <Skeleton className="h-12 w-3/4" />
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-6 w-1/2" />
        </div>
      </div>
      <div className="bg-card shadow-lg rounded-xl overflow-hidden">
        <div className="flex flex-col items-center justify-center p-6 h-[200px] space-y-2">
          <Skeleton className="rounded-full w-24 h-24 sm:w-28 sm:h-28" />
          <Skeleton className="h-4 w-1/3 mt-1" />
          <Skeleton className="h-6 w-1/2" />
          <Skeleton className="h-4 w-1/4" />
        </div>
      </div>
    </div>
  </div>
);

export default TeamLoadingSkeleton;
