/**
 * TeamLoadingSkeleton.tsx
 *
 * Displays a loading skeleton for team detail pages.
 * Wraps EntityLoadingSkeleton for team-specific loading UI.
 *
 * Exports:
 *   - TeamLoadingSkeleton: React.FC for team loading state display.
 */
import React from "react";
import EntityLoadingSkeleton from "../common/EntityLoadingSkeleton";

/**
 * Displays a loading skeleton for team detail pages.
 *
 * @returns The rendered team loading skeleton.
 */
const TeamLoadingSkeleton: React.FC = () => <EntityLoadingSkeleton />;

export default TeamLoadingSkeleton;
