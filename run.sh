#!/bin/bash
# vim: tabstop=4 shiftwidth=4 expandtab

# Shortcuts

key="ChangeThisKey"
pkg="NuGetTest"
vers="0.0.1"
src="http://localhost:5000"
file="./tests/data/NuGetTest.0.0.1.nupkg"
nuget_exe="/home/dthor/temp/nuget.exe"

# Help Docs.
usage () {
    echo $1
    echo "Usage:"
    echo "   run.sh --list"
    echo "      List all packages"
    echo "   run.sh --delete"
    echo "      Delete the NuGetTest v0.0.1 package"
    echo "   run.sh --push [file]"
    echo "      Push FILE to the server. Defaults to 'NuGetTest.0.0.1.nupkg'"
    echo ""
}


case "$1" in
    --list)
        echo "Listing!"
        (set -x; mono $nuget_exe list -Source $src -Verbosity detailed -AllVersions -Prerelease)
        ;;
    --delete)
        echo "Deleting!"
        (set -x; mono $nuget_exe delete -ApiKey $key -Source $src -Verbosity detailed -NonInteractive $pkg $vers)
        ;;
    --push)
        echo "Pushing!"
        (set -x; mono $nuget_exe push -ApiKey $key -Source $src -Verbosity detailed $file)
        ;;
    -h)
        usage ""
        ;;
    --help)
        usage ""
        ;;
    *)
        usage "Invalid Argument: $1"
        ;;
esac

