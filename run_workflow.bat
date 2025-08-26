@echo off
echo 🚀 FOOT SEGMENTATION ANNOTATION WORKFLOW
echo ========================================

echo Step 1: Auto-generate initial masks...
python auto_masking.py

echo Step 2: Setup team annotation...
python annotation_system.py

echo Step 3: Team members annotate assigned images
echo   - Each member runs: labelme annotation_workspace/[member_name]/assigned/
echo   - Save masks to: annotation_workspace/[member_name]/masks/

echo Step 4: Collect and merge results...
python merge_annotations.py

echo Step 5: Prepare final dataset...
python data_preparation.py

echo ✅ Workflow complete! Ready for training.
pause