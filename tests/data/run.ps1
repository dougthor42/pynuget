<#

.SYNOPSIS
Make it easier to test the PyNuGet program.

.DESCRIPTION
Provides 3 flags, 'List', 'Delete', and 'Push', which will interact with the
PyNuGet server.

.PARAMETER List
    List all of the packages on the PyNuGet Server
.PARAMETER Delete
    Delete the "NuGetTest v0.0.1" package from the PyNuGet Server
.PARAMETER Push
    Push the "NuGetTest.0.0.1.nupkg" file to the PyNuGet Server

.EXAMPLE
.\run.ps1 -List
.\run.ps1 -Delete
.\run.ps1 -Push

#>

param (
    [switch] $list,
    [switch] $delete,
    [switch] $push,
    [string] $file = ".\NuGetTest.0.0.1.nupkg"
)

$key = "ChangeThisKey"
$pkg = "NuGetTest"
$vers = "0.0.1"
$source = "http://localhost:5000"

if ($list) {
    Write-Host "Listing!"
    nuget.exe list -Source $source -Verbosity detailed -AllVersions -Prerelease
}

if ($delete) {
    Write-Host "Deleting!"
    nuget.exe delete -ApiKey $key -Source $source -Verbosity detailed -NonInteractive $pkg $vers
}

if ($push) {
    Write-Host "Pushing!"
    nuget.exe push -ApiKey $key -Source $source -Verbosity detailed $file
}
