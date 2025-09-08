'use client';

import { useEffect } from 'react';
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';

export default function AgGridProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Register AG Grid modules on the client side
    ModuleRegistry.registerModules([AllCommunityModule]);
  }, []);

  return <>{children}</>;
}

