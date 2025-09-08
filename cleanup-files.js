const fs = require('fs');
const path = require('path');

// Files to keep (core project files)
const keepFiles = [
  'package.json',
  'package-lock.json',
  'next.config.ts',
  'next-env.d.ts',
  'tsconfig.json',
  'postcss.config.mjs',
  'eslint.config.mjs',
  'README.md',
  'SUPABASE_SETUP.md',
  'requirements.txt',
  'prisma',
  'app',
  'components',
  'lib',
  'styles',
  'public',
  'supabase',
  'data',
  'data_import',
  'database_backups',
  'node_modules',
  '.git'
];

// Files to delete (temporary testing/debugging files)
const filesToDelete = [
  // Betting data analysis files
  'analyze-betting-data.js',
  'analyze-connection-errors.js',
  'check-betting-coverage.js',
  'check-betting-date-range.js',
  'check-betting-import-results.js',
  'check-season-format.js',
  
  // Date range checking files
  'check-2015-16-dates.js',
  'check-date-range.js',
  'check-games-2014-2015.js',
  'check-games-date-range.js',
  'find-2015-data.js',
  'find-actual-overlap.js',
  'compare-date-ranges.js',
  
  // Database checking files
  'check-db-size.js',
  'check-db.js',
  'check-game-types.js',
  'check-games-structure.js',
  'check-games-table.js',
  'check-player-stats-table.js',
  'check-players-table.js',
  
  // Team matching files
  'check-team-matching.js',
  'debug-corrected-mapping.js',
  'debug-team-mapping.js',
  
  // Import testing files
  'create-betting-import.js',
  'import-betting-correct.js',
  'import-betting-data.js',
  'import-betting-filtered.js',
  'import-by-season.js',
  'import-player-stats-streaming.js',
  'import-player-stats.js',
  'optimized-betting-import.js',
  
  // Test files
  'test-2015-matching.js',
  'test-betting-import.js',
  'test-broad-date-range.js',
  'test-correct-import.js',
  'test-filtered-import.js',
  'test-fixed-mapping.js',
  'test-full-scale-errors.js',
  'test-larger-import.js',
  'test-optimized-import.js',
  'test-overlap-matching.js',
  'test-overlap-period.js',
  'test-recent-dates.js',
  'test-recent-seasons.js',
  'test-single-season.js',
  'test-small-import.js',
  
  // Debug files
  'debug-import-errors.js',
  'debug-matching.js',
  
  // Python files (if any)
  'reimport_player_stats.py',
  
  // Cleanup script itself
  'cleanup-files.js'
];

function deleteFile(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      console.log(`✅ Deleted: ${filePath}`);
      return true;
    } else {
      console.log(`⚠️  Not found: ${filePath}`);
      return false;
    }
  } catch (error) {
    console.error(`❌ Error deleting ${filePath}:`, error.message);
    return false;
  }
}

function cleanupFiles() {
  console.log('🧹 Starting file cleanup...\n');
  
  let deletedCount = 0;
  let errorCount = 0;
  
  console.log('📁 Files to delete:');
  filesToDelete.forEach(file => {
    console.log(`  - ${file}`);
  });
  
  console.log('\n🗑️  Deleting files...\n');
  
  filesToDelete.forEach(file => {
    const success = deleteFile(file);
    if (success) {
      deletedCount++;
    } else {
      errorCount++;
    }
  });
  
  console.log('\n📊 Cleanup Summary:');
  console.log(`✅ Successfully deleted: ${deletedCount} files`);
  console.log(`❌ Errors: ${errorCount} files`);
  console.log(`📁 Total files processed: ${filesToDelete.length}`);
  
  // Check remaining files
  console.log('\n📋 Remaining files in project:');
  const remainingFiles = fs.readdirSync('.')
    .filter(file => !file.startsWith('.') && !keepFiles.includes(file))
    .filter(file => !filesToDelete.includes(file));
  
  if (remainingFiles.length > 0) {
    console.log('⚠️  Additional files found:');
    remainingFiles.forEach(file => {
      console.log(`  - ${file}`);
    });
  } else {
    console.log('✅ Project is clean!');
  }
  
  console.log('\n🎉 Cleanup completed!');
}

// Run cleanup
cleanupFiles();
