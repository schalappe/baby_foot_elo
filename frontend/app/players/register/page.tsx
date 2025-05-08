"use client";

import React from 'react';
import PlayerRegistrationForm from '@/components/PlayerRegistrationForm';

const PlayerRegistrationPage: React.FC = () => {
  return (
    <div className="container mx-auto p-4 flex justify-center">
      <div className="w-full max-w-lg">
          <PlayerRegistrationForm />
      </div>
    </div>
  );
};

export default PlayerRegistrationPage;
