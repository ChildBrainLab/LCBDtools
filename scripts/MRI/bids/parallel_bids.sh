for sub in `cat $4`

do
    mkdir ~/input/sub-$sub
    mkdir ~/input/sub-$sub/ses-$3
    mkdir ~/input/sourcedata/$sub
    mkdir ~/input/sourcedata/$sub/$3

    aws s3 cp --recursive $1/sub-$sub/ses-$3 ~/input/sourcedata/$sub/$3

    bidskit -d ~/input/ --no-anon --subject $sub --multiecho --bind-fmaps

    rm -r ~/input/sourcedata/$sub    

    aws s3 sync ~/input/ $2/

    rm -r ~/input/sub-$sub
done
