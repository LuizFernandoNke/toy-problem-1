import os
import sys
from pathlib import Path

# Diretórios base
ROOT_DIR = Path(__file__).resolve().parent.parent
CASE_DIR = ROOT_DIR / "template_case"


def setup_control_dict(case_dir: Path):
    """Gera o arquivo system/controlDict."""
    content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      / F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /  O peration     | Version:  2606                                  |
|   \\\\  /   A nd            | Website:  www.openfoam.com                      |
|    \\\\/    M anipulation   |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     interFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         10;
deltaT          1e-2;
writeControl    timeStep;
writeInterval   1;
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
adjustableTimeStep  on;
maxCo          0.5;
maxAlphaCo     1;

// ************************************************************************* //
"""
    system_dir = case_dir / "system"
    system_dir.mkdir(parents=True, exist_ok=True)
    with open(system_dir / "controlDict", "w", encoding="utf-8") as f:
        f.write(content)


def setup_fv_schemes(case_dir: Path):
    """Gera o arquivo system/fvSchemes com a entrada wallDist necessária."""
    content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      / F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /  O peration     | Version:  2606                                  |
|   \\\\  /   A nd            | Website:  www.openfoam.com                      |
|    \\\\/    M anipulation   |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    div(rhoPhi,U)   Gauss linearUpwind grad(U);
    div(phi,alpha)  Gauss vanLeer;
    div(phirb,alpha) Gauss linear;
    div(phi,k)          Gauss linearUpwind grad(k);
    div(phi,omega)      Gauss linearUpwind grad(omega);
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method          meshWave;
}

// ************************************************************************* //
"""
    system_dir = case_dir / "system"
    system_dir.mkdir(parents=True, exist_ok=True)
    with open(system_dir / "fvSchemes", "w", encoding="utf-8") as f:
        f.write(content)


def setup_fv_solution(case_dir: Path):
    """Gera o arquivo system/fvSolution."""
    content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      / F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /  O peration     | Version:  2606                                  |
|   \\\\  /   A nd            | Website:  www.openfoam.com                      |
|    \\\\/    M anipulation   |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    "alpha.water.*"
    {
        nAlphaCorr      2;
        nAlphaSubCycles 1;
        cAlpha          1;

        MULESCorr       yes;
        nLimiterIter    5;

        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-8;
        relTol          0;
    }

    "pcorr.*"
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-5;
        relTol          0;
    }

    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-07;
        relTol          0.05;
    }

    p_rghFinal
    {
        $p_rgh;
        relTol          0;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-06;
        relTol          0;
    }

    omega
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }

    omegaFinal
    {
        $omega;
        tolerance       1e-07;
        relTol          0;
    }

    k
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }

    kFinal
    {
        $k;
        tolerance       1e-07;
        relTol          0;
    }
}

PIMPLE
{
    momentumPredictor   no;
    nOuterCorrectors    1;
    nCorrectors         3;
    nNonOrthogonalCorrectors 0;
}

relaxationFactors
{
    equations
    {
        ".*" 1;
    }
}

// ************************************************************************* //
"""
    system_dir = case_dir / "system"
    system_dir.mkdir(parents=True, exist_ok=True)
    with open(system_dir / "fvSolution", "w", encoding="utf-8") as f:
        f.write(content)


def setup_decompose_par(case_dir: Path, num_processors: int = 10):
    """Gera o decomposeParDict usando o método Scotch com o cabeçalho FoamFile correto."""
    content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      / F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /  O peration     | Version:  2606                                  |
|   \\\\  /   A nd            | Website:  www.openfoam.com                      |
|    \\\\/    M anipulation   |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      decomposeParDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains  {num_processors};

method              scotch;

// ************************************************************************* //
"""
    system_dir = case_dir / "system"
    system_dir.mkdir(parents=True, exist_ok=True)
    with open(system_dir / "decomposeParDict", "w", encoding="utf-8") as f:
        f.write(content)


def main():
    setup_control_dict(CASE_DIR)
    setup_fv_schemes(CASE_DIR)
    setup_fv_solution(CASE_DIR)
    setup_decompose_par(CASE_DIR, num_processors=10)
    print("System files (controlDict, fvSchemes, fvSolution, decomposeParDict) generated successfully.")


if __name__ == "__main__":
    main()