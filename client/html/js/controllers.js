var matomatControllers = angular.module('matomatControllers', []);

matomatControllers.controller('loginCtrl', ['$scope','authenticator','$rootScope',
		function ($scope,authenticator,$rootScope) {
			authenticator.forward_if_valid('/balance');
			$scope.setUser=function (user,pass) {
				authenticator.user=user;
				authenticator.pass=pass;
				if ($scope.remember){
					authenticator.remember();
				}
				authenticator.forward_if_valid('/balance');
			}
}]);

matomatControllers.controller('detailCtrl', ['$scope', '$http', 'authenticator',
		function($scope,$http, authenticator) {
			authenticator.login_if_invalid();
			$scope.user=authenticator.user;
			$scope.pass=authenticator.pass;
			$scope.loadDetails=function(){
				var url="api/"+$scope.user+"/details";
				$http.get(url,{headers:{pass:$scope.pass}})
					.success(function(data){
						$scope.details=data;
					});
			}
			$scope.loadDetails();
}]);

matomatControllers.controller('itemsCtrl', ['$scope', '$http', 'authenticator','$log',
		function($scope,$http, authenticator,$log) {
			authenticator.login_if_invalid();
			$scope.user=authenticator.user;
			$scope.pass=authenticator.pass;
			$scope.delete=function(id){
				var url="api/"+$scope.user+"/items/"+id;
				$http.delete(url,{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.loadItems();
				});
			}
			$scope.create=function(){
				var url="api/"+$scope.user+"/items";
				var data=$scope.new_item;
				$http.post(url,data,{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.loadItems();
				})
				.error(function(data){
					$scope.loadItems();
				});
			}
			$scope.save=function(id){
				var url="api/"+$scope.user+"/items/"+id;
				var data={};
				for (var i in $scope.items){
					var v=$scope.items[i];
					if (v.id==id){
						data={"name":v.name,"price":v.price};
					}
				}
					$log.log(data);
				$http.put(url,data,{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.loadItems();
				})
				.error(function(data){
					$scope.loadItems();
				});
			}
			$scope.loadItems=function(){
				$http.get("api/items")
					.success(function(data){
						$scope.items=data;
					});
				$scope.new_item={"name":"","price":""};
			}
			$scope.loadItems();
}]);

matomatControllers.controller('userCtrl', ['$scope', '$http', 'authenticator',
		function($scope,$http, authenticator) {
			authenticator.login_if_invalid();
			$scope.user=authenticator.user;
			$scope.pass=authenticator.pass;
			$scope.new_user=$scope.user;

			$scope.create_user=function(){
				if ($scope.pass1!=$scope.pass2){
					$scope.message="Zweiteingabe des Passwortes stimmt nicht";
					return;
				}
				var url="api/"+$scope.user+"/user";
				var data={"username":$scope.new_user,"password":$scope.pass1};
				$http.post(url,data,{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.message="Benutzer angelegt";
				})
				.error(function(data){
					$scope.message="Benutzer konnte nicht angelegt werden";
				});
			}
}]);

matomatControllers.controller('balanceCtrl', ['$scope', '$http', '$location', 'authenticator','$rootScope',
		function($scope,$http,  $location, authenticator,$rootScope) {
			authenticator.login_if_invalid();
			$scope.user=authenticator.user;
			$scope.pass=authenticator.pass;
			$scope.pay=function(amount){
				var url="api/"+$scope.user+"/pay";
				$http.post(url,Math.round(amount*100),{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.message=""+amount+" EUR eingezahlt";
					$scope.loadBalance();
				})
				.error(function(data){
					$scope.message="Einzahlen fehlgeschlagen";
				});
			};
			$scope.payexternal=function(amount){
				var url="api/"+$scope.user+"/payexternal";
				$http.post(url,amount*100,{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.message=""+amount+" EUR per Lastschrift eingezahlt";
					$scope.loadBalance();
				})
				.error(function(data){
					$scope.message="Einzahlen fehlgeschlagen";
				});
			};

			$scope.transfer=function(amount,recipient){
				var url="api/"+$scope.user+"/transfer";
				data={'amount':amount*100,'recipient':recipient};
				$http.post(url,data,{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.message=""+amount+"EUR überwiesen";
					$scope.loadBalance();
				})
				.error(function(data){
					$scope.message="Überweisung fehlgeschlagen";
				});
			};

			$scope.undo=function(){
				var url="api/"+$scope.user+"/undo";
				$http.post(url,"",{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.message="letzte Aktion rueckgaengig gemacht";
					$scope.loadBalance();
				})
				.error(function(data){
					$scope.message="letzte Aktion konnte nicht rückgaengig gemacht werden";
				});
			};

			$scope.buy=function(item){
				var url="api/"+$scope.user+"/buy";
				$http.post(url,item,{headers:{pass:$scope.pass}})
				.success(function(data){
					$scope.loadBalance();
					for (i in $scope.items){
						it=$scope.items[i];
						if (it.id==item){
							$scope.message="Ein "+it.name+" fuer "+it.price/100+"EUR gekauft";
							break;
						}
					}
				})
				.error(function(data){
					$scope.message="Kauf fehlgeschlagen";
				});
			};

			$scope.loadBalance=function(){
				var url="api/"+$scope.user+"/balance";
				$http.get(url,{headers:{pass:$scope.pass}})
					.success(function(data){
						$scope.balance=data;
					})
					.error(function(data,response){
						$scope.message="Konnte anktuellen Kontostand nicht empfangen";
					}
					);
			}

			$http.get("api/items")
				.success(function(data){
					$scope.items=data;
				});
			$scope.loadBalance();
		}]);
