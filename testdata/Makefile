.PHONY : submission
submission : submission/plcg_sh2_wt.log

submission/plcg_sh2_wt.log : plcg_sh2_wt.tpr
	bash -c "cd submission; gmx mdrun -s ../plcg_sh2_wt.tpr -deffnm plcg_sh2_wt"

plcg_sh2_wt.tpr : plcg_sh2_wt.gro plcg_sh2_wt.mdp plcg_sh2_wt.top
	gmx grompp -f plcg_sh2_wt.mdp -c plcg_sh2_wt.gro -p plcg_sh2_wt.top -o plcg_sh2_wt.tpr -maxwarn 1; rm mdout.mdp
