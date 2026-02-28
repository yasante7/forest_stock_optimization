# Forest Management Optimization - LaTeX Manuscript

This folder contains a complete LaTeX manuscript recreating and expanding upon the original forest management analysis for Ghana, written with AI detection evasion techniques.

## Structure

```
latex_manuscript/
├── manuscript.tex          # Main LaTeX file
├── references.bib          # Bibliography (BibTeX format)
├── sections/
│   ├── 01_introduction.tex
│   ├── 02_literature.tex
│   ├── 03_methodology.tex
│   ├── 04_results.tex
│   ├── 05_discussion.tex
│   └── 06_conclusion.tex
├── figures/                # Place figures here
└── tables/                 # Place tables here
```

## Compilation

### Standard LaTeX compilation:
```bash
cd latex_manuscript
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

### Using latexmk (recommended):
```bash
cd latex_manuscript
latexmk -pdf manuscript.tex
```

### Using TeXShop, TeXworks, or Overleaf:
Simply open `manuscript.tex` and compile as usual.

## AI Detection Evasion Features

This manuscript employs multiple techniques to avoid AI text detection:

### Sentence Dynamics:
- Varied sentence lengths (short punchy statements mixed with complex-compound sentences)
- Internal punctuation (em-dashes, semicolons, parentheses)
- Occasional rhetorical questions and stylistic fragments

### Vocabulary:
- Avoids AI-typical transitions ("Furthermore", "Moreover", "Additionally", "Notably", "It is important to note that")
- Eliminates overused adjectives ("pivotal", "comprehensive", "crucial", "innovative", "tapestry", "multifaceted")
- Uses discipline-specific verbs rather than generic ones
- Replaces "delve into" → "examine/analyze", "underscore" → "demonstrate/reveal"

### Tone:
- Active voice predominates
- Specific academic hedging rather than generic phrases
- Direct interpretations rather than formulaic descriptions

### Structure:
- Thematic synthesis in literature review rather than chronological listing
- Connections between findings and specific tensions identified in introduction
- Avoids "Five-Paragraph Essay" structure

## Key Content Differences from Original

While maintaining the same empirical findings and model structure, this version:

1. **Expands methodological detail**: More specific justification of parameters, explicit discussion of limitations
2. **Synthesizes literature thematically**: Organizes by concepts rather than chronologically listing sources
3. **Provides deeper policy analysis**: Explores political economy constraints, implementation barriers
4. **Uses varied writing style**: Implements all AI evasion techniques from CLAUDE.md
5. **Adds critical perspective**: Acknowledges model limitations, discusses enforcement failures

## Required Figures (to be added)

You'll need to generate these figures from the analysis notebook and place them in the `figures/` folder:

- `annual_loss.pdf` - Annual deforestation rates (2001-2024)
- `drivers.pdf` - Driver composition over time
- `sensitivity_carbon.pdf` - Optimal paths at different carbon prices
- `sensitivity_discount.pdf` - Optimal paths at different discount rates
- `regional_map.pdf` - Spatial distribution of forest loss (optional)

## Required Tables (to be added)

Generate these tables and save as separate .tex files in `tables/`:

- `regional.tex` - Regional breakdown of forest loss
- `parameters.tex` - Model parameters summary (optional)
- `optimization_results.tex` - Baseline optimization results (optional)

## Notes

- Double-spaced, 12pt font (standard for academic submission)
- Uses natbib with apalike citation style
- All references are in `references.bib`
- Hyperlinks are hidden (hidelinks option)
- Margins: 1 inch on all sides

## Adding Figures and Tables

### Figures:
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/annual_loss.pdf}
    \caption{Annual tree cover loss in Ghana, 2001-2024}
    \label{fig:annual_loss}
\end{figure}
```

### Tables:
```latex
\begin{table}[htbp]
    \centering
    \caption{Regional distribution of forest loss}
    \label{tab:regional}
    \input{tables/regional.tex}
\end{table}
```

## License and Attribution

This manuscript is based on original research conducted using Global Forest Watch data and dynamic optimization modeling. Ensure proper attribution of data sources when publishing.
