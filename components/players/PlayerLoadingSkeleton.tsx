/**
 * PlayerLoadingSkeleton.tsx
 *
 * Displays a loading skeleton for player detail pages.
 * Wraps EntityLoadingSkeleton for player-specific loading UI.
 *
 * Exports:
 *   - PlayerLoadingSkeleton: React.FC for player loading state display.
 */
import React from "react";
import EntityLoadingSkeleton from "../common/EntityLoadingSkeleton";

/**
 * Displays a loading skeleton for player detail pages.
 * @returns The rendered player loading skeleton
 */
const PlayerLoadingSkeleton: React.FC = () => <EntityLoadingSkeleton />;

export default PlayerLoadingSkeleton;
