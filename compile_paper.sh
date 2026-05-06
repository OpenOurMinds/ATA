#!/bin/bash

# ATA Research Paper Compilation Script
# Compiles the LaTeX research paper to PDF

echo "📄 Compiling ATA Research Paper..."

# Check if pdflatex is installed
if ! command -v pdflatex &> /dev/null
then
    echo "❌ Error: pdflatex is not installed"
    echo "   Install TeX Live or MacTeX to compile LaTeX documents"
    exit 1
fi

# Check if bibtex is installed
if ! command -v bibtex &> /dev/null
then
    echo "❌ Error: bibtex is not installed"
    echo "   Install TeX Live or MacTeX to compile LaTeX documents"
    exit 1
fi

# Create temporary directory for compilation
TEMP_DIR="latex_temp"
mkdir -p "$TEMP_DIR"

# Copy files to temp directory
cp research_paper.tex "$TEMP_DIR/"
cp references.bib "$TEMP_DIR/"
cd "$TEMP_DIR"

# Compile LaTeX
echo "   Step 1: First pdflatex pass..."
pdflatex -interaction=nonstopmode research_paper.tex > /dev/null 2>&1

echo "   Step 2: Running bibtex..."
bibtex research_paper > /dev/null 2>&1

echo "   Step 3: Second pdflatex pass..."
pdflatex -interaction=nonstopmode research_paper.tex > /dev/null 2>&1

echo "   Step 4: Third pdflatex pass..."
pdflatex -interaction=nonstopmode research_paper.tex > /dev/null 2>&1

# Check if PDF was created
if [ -f "research_paper.pdf" ]; then
    # Move PDF to parent directory
    mv research_paper.pdf ../
    echo "✅ PDF compiled successfully: research_paper.pdf"
    
    # Clean up temporary files
    cd ..
    rm -rf "$TEMP_DIR"
    
    # Show PDF size
    SIZE=$(du -h research_paper.pdf | cut -f1)
    echo "   File size: $SIZE"
else
    echo "❌ Error: PDF compilation failed"
    echo "   Check the log file for errors"
    cd ..
    rm -rf "$TEMP_DIR"
    exit 1
fi
