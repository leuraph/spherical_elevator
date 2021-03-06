#define _USE_MATH_DEFINES // for Cpp

#include <iostream>
#include <vector>
#include <cstdlib>
#include <cmath>
#include <stdio.h>
#include <boost/numeric/odeint/integrate/integrate.hpp>

/*---------------*/
/* EXAMPLE SETUP */
/*---------------*/
namespace simul{

	typedef double data_t;

	static const data_t omega = 2. * M_PI * 0.5;
	static const data_t R0 = 1.;
	static const data_t l0 = 3.;

	void acquire_R(data_t* R, const double t)
	{
		R[0] = R0 * std::cos(omega*t);
		R[1] = R0 * std::sin(omega*t);
		R[2] = 0.;
	}

	void acquire_Rdd(data_t* Rdd, const double t)
	{
		Rdd[0] = - omega*omega* R0 * std::cos(omega*t);
		Rdd[1] = - omega*omega* R0 * std::sin(omega*t);
		Rdd[2] = 0.;
	}

	void acquire_l(data_t* l, const double t)
	{
		l[0] = l0;
	}

	void acquire_ld(data_t* ld, const double t)
	{
		ld[0] = 0.;
	}

}

static double tmin = 0.;
static double tmax = 10.;
static int N = 10000;
static simul::data_t g = 9.81;

static double dt = ( tmax - tmin ) / (double)N;
static simul::data_t *R, *Rdd, *l, *ld, *r;
static int nt;
static double t;
static size_t steps;

void acquire_bc(simul::data_t *R, simul::data_t *Rdd, simul::data_t *l, simul::data_t *ld, const double t)
{
	simul::acquire_R(R, t);
	simul::acquire_Rdd(Rdd, t);
	simul::acquire_l(l, t);
	simul::acquire_ld(ld, t);
}

/*--------------*/
/* ODEINT SETUP */
/* ------------ */
typedef std::vector<simul::data_t> state_type;

void RHS(const state_type& z, state_type& dzdt, const double t)
{
	simul::data_t z1 = z[0]; // theta(t)
    simul::data_t z2 = z[1]; // phi(t)
    simul::data_t z3 = z[2]; // \dot{theta}(t)
    simul::data_t z4 = z[3]; // \dot{phi}(t)

    simul::data_t z1d = z[2]; // \dot{z}_1 = z_3
    simul::data_t z2d = z[3]; // \dot{z}_2 = z_4

    dzdt[0] = z3; // \dot{z}_1 = z_3
    dzdt[1] = z4; // \dot{z}_2 = z_4
    dzdt[2] = -1./l[0]*(
          g*std::sin(z1)
        - std::cos(z1)*l[0]*std::sin(z1)*z2d*z2d
        + 2.*ld[0]*z1d
        + std::cos(z2)*std::cos(z1)*Rdd[0] + std::cos(z1)*std::sin(z2)*Rdd[1]
        + std::sin(z1)*Rdd[2]
    );

    /* 
    EL eqs. give something like sin(theta)(... + phi'') = 0, i.e. if theta==0, we can't divide by sin(theta).
    This is a mathematical artifact of the spherical coordinates as (x, y, z): R^2 -> R^3 is
    not injective, i.e. if theta mod pi == 0, all points get mapped either to the top or
    the bottom of the sphere.
    However, it should be more or less intuitive to notice that, if theta==0, seting phi''=0
    comes with no physically relevant implications.
    */
    if ( std::fmod(z1, M_PI) == 0)
    {
    	dzdt[3] = 0;
    }
    else
    {
        dzdt[3] = 1./l[0]*(
			- 2.*ld[0]*z2d
            - 2.*(1./std::tan(z1))*l[0]*z1d*z2d
            + (1./std::sin(z1))*std::sin(z2)*Rdd[0]
            - std::cos(z2)/std::sin(z1)*Rdd[1]
        );
    }
}

/**
 * updates the euclidean coordinates r=(x,y,z) of the elevators position given theta and phi
 * 
 * @param r: position of the elevator to be updated
 * @param z: current angles and their derivatives, i.e. z=(theta, phi, theta', phi')
*/
void update_euclidean_coordinates(simul::data_t* r, state_type& z)
{
	simul::data_t theta = z[0]; // spherical coordinates, angle theta measured from bottom of sphere
	simul::data_t phi = z[1]; // spherical coordinates, angle phi measred from x-axis

	r[0] = R[0] + l[0] * std::cos( phi )*std::sin( theta );
	r[1] = R[1] + l[0] * std::sin( phi )*std::sin( theta );
	r[2] = R[2] - l[0] * std::cos( theta );
}

void save_cnfg(FILE* fdat)
{
	fwrite(&tmin, sizeof(double), 1, fdat);
	fwrite(&tmax, sizeof(double), 1, fdat);
	fwrite(&dt, sizeof(double), 1, fdat);
	fwrite(&N, sizeof(int), 1, fdat);
}

int main(int argc, char const *argv[])
{
	/*-------------------*/
	/* memory allocation */
	/*-------------------*/
	R = (simul::data_t*)malloc(3*sizeof(simul::data_t));
	Rdd = (simul::data_t*)malloc(3*sizeof(simul::data_t));
	l = (simul::data_t*)malloc(sizeof(simul::data_t));
	ld = (simul::data_t*)malloc(sizeof(simul::data_t));
	r = (simul::data_t*)malloc(3*sizeof(simul::data_t));
	state_type z; // std::vector manages its own memory
	z.resize(4);
	z.reserve(4);

	/* files to hold position of sphere R(t) and numerical results for r(t) */
	FILE* fdat_R = fopen("results/R.dat", "wb");
	FILE* fdat_r = fopen("results/r.dat", "wb");

	/* saving temporal configuration for plotting purposes only */
	FILE* fdat_cnfg = fopen("results/cnfg.dat", "wb");
	save_cnfg(fdat_cnfg);
	fclose(fdat_cnfg);

	/* this represenets the timeloop, where dt is to be specified by the game itself */
	for(t=tmin; t<tmax; t+=dt)
	{
		/*----------------------------------------------------*/
		/* update boundary conditions, i.e. R, Rdd, l, and ld */
		/*----------------------------------------------------*/
		acquire_bc(R, Rdd, l, ld, t);

		/*-----------------------------------------------------------*/
		/* update z, then update corresponding euclidean coordinates */
		/*-----------------------------------------------------------*/
		steps = boost::numeric::odeint::integrate( RHS, z , t , t+dt , dt/10. );
		update_euclidean_coordinates(r, z);

		/*-----------------*/
		/* save the result */
		/*-----------------*/
		fwrite(&(r[0]), sizeof(simul::data_t), 1, fdat_r);
		fwrite(&(r[1]), sizeof(simul::data_t), 1, fdat_r);
		fwrite(&(r[2]), sizeof(simul::data_t), 1, fdat_r);
		fwrite(&(R[0]), sizeof(simul::data_t), 1, fdat_R);
		fwrite(&(R[1]), sizeof(simul::data_t), 1, fdat_R);
		fwrite(&(R[2]), sizeof(simul::data_t), 1, fdat_R);
	}

	/* clean up */
	free(R);
	free(Rdd);
	free(l);
	free(ld);
	free(r);
	z.resize(0);
	fclose(fdat_R);
	fclose(fdat_r);

	return 0;
}