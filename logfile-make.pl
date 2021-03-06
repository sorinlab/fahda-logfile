#!/usr/bin/env perl

use strict;
use warnings;

use Cwd;
use FindBin qw($Bin);
use Getopt::Long qw(HelpMessage :config pass_through);
use lib "$Bin/lib";
use List::Util qw(max);
use Share::DirUtil qw(get_dirs);
use Share::Fahda qw(get_xtc_file get_max_dir_number);

GetOptions("help|h" => sub { print HelpMessage(0) });

my $Project_Dir     = $ARGV[0] or die "[FATAL]  Project directory must be specified\n";
my $Output_Filename = $ARGV[1] or die "[FATAL]  Output filename must be specified\n";

$Output_Filename = "${\getcwd()}/$Output_Filename";
if (-e $Output_Filename) {
    unlink $Output_Filename or die "[FATAL]  Cannot delete $Output_Filename: $!\n";
}

$Project_Dir =~ s/\/$//;    # Remove trailing slash if any
my ($Project_Number) = $Project_Dir =~ m/(\d+$)/;
my $Project_Path = "${\getcwd()}/$Project_Dir";
generate_logfile($Project_Path, $Project_Number);

sub generate_logfile {
    my ($project_path, $project_number) = @_;

    chdir($project_path);

    my @run_dirs = get_dirs($project_path, '^RUN\d+$');
    if (scalar(@run_dirs) == 0) {
        print STDOUT "[INFO]  No RUN found\n";
        return;
    }

    for (my $run_number = 0 ; $run_number <= get_max_dir_number(@run_dirs) ; $run_number++) {
        my $run_dir = "RUN$run_number";
        if (not -d $run_dir) { next; }

        chdir $run_dir;

        my @clone_dirs = get_dirs("$project_path/$run_dir", '^CLONE\d+$');
        if (scalar(@clone_dirs) == 0) {
            print STDOUT "[INFO]  No CLONE found in $run_dir\n";
            next;
        }

        foreach (my $clone_number = 0 ; $clone_number <= get_max_dir_number(@clone_dirs) ; $clone_number++) {
            my $clone_dir = "CLONE$clone_number";
            if (not -d $clone_dir) { next; }

            chdir $clone_dir;

            my $clone_path = "$project_path/$run_dir/$clone_dir";
            my $xtc_file   = get_xtc_file($clone_path);
            if (not defined $xtc_file || not -e $xtc_file) {
                print STDOUT "[WARN]  Skipped--XTC file $xtc_file not found\n";
                next;
            }

            my $all_frames_pdb        = generate_all_frames_pdb($xtc_file);
            my $timestamps_collection = parse_all_frames_pdb($all_frames_pdb);
            my $log_string            = prepare_log_string($project_number, $run_number, $clone_number, $timestamps_collection);

            open(my $OUT, ">>", $Output_Filename) or die "[FATAL]  $Output_Filename: $!\n";
            print $OUT $log_string;
            close($OUT);

            chdir "..";
        }

        chdir "..";
    }
}

sub generate_all_frames_pdb {
    my ($xtc_file) = @_;

    my $pdb_file = $xtc_file;
    $pdb_file =~ s/\.xtc$/.pdb/;
    if (-e $pdb_file) { return $pdb_file; }

    # `echo 1` to select the RNA (protein) group
    my $trjconv_cmd = "echo 1 | trjconv -s frame0.tpr -f $xtc_file -o $pdb_file  2>&1";
    print STDOUT "Executing `$trjconv_cmd`\n";
    print STDOUT `$trjconv_cmd` . "\n";

    return $pdb_file;
}

sub parse_all_frames_pdb {
    my ($all_frames_pdb) = @_;
    my %timestamps = ();

    open(my $ALL_FRAME_PDB, '<', $all_frames_pdb) or die "[FATAL]  $all_frames_pdb: $!\n";
    while (my $line = <$ALL_FRAME_PDB>) {
        if ($line !~ m/^TITLE/) { next; }

        chomp(my @fields = split(/t=\s/, $line));
        my $timestamp = int($fields[1]);
        if (not defined $timestamps{$timestamp}) {
            $timestamps{$timestamp} = 1;
        }
        else {
            $timestamps{$timestamp} += 1;
        }
    }
    close($ALL_FRAME_PDB);

    return \%timestamps;
}

sub prepare_log_string {
    my ($project_number, $run_number, $clone_number, $timestamps_collection) = @_;
    my $log_string = "";

    foreach my $timestamp (sort { $a <=> $b } keys %{$timestamps_collection}) {
        $log_string .= sprintf("%4d    %3d    %3d    %6d\n", $project_number, $run_number, $clone_number, $timestamp);
    }

    return $log_string;
}

=head1 NAME

logfile-make.pl - Make F@H logfile

=head1 SYNOPSIS

logfile-make.pl <project_dir> <output.log>

Generates the F@H logfile.

=cut
